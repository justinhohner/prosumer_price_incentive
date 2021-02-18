
import os
import csv
import json
from datetime import date, datetime, timedelta

from geopy.geocoders import Nominatim

import urllib3
urllib3.disable_warnings()

import ResourceTools as tools

#https://github.com/NREL/pysam/blob/master/Examples/FetchResourceFileExample.py
nrel_api_key = os.getenv("NREL_API_KEY")
nrel_api_email = os.getenv("NREL_API_EMAIL")
nsrdbfetcher = tools.FetchResourceFiles(
                tech='solar',
                nrel_api_key=nrel_api_key,
                nrel_api_email=nrel_api_email)


elasticity_table = {}
regional_elasticities = {}
with open('short-run price elasticities for the residential electricity market.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        regional_elasticities[row['Division']] = float(row['elasticity'])

with open('us census bureau regions and divisions.csv') as csvfile:
    #State,State Code,Region,Division
    reader = csv.DictReader(csvfile)
    for row in reader:
        elasticity_table[row['State']] = regional_elasticities[row['Division']]

try:
    with open('locations.json', 'r') as jsonfile:
        LOCATIONS = json.load(jsonfile)
except FileNotFoundError:
    LOCATIONS = {}

def lookup_location(lat, lon):
    lat_lon = "%s, %s" % (lat, lon)
    if lat_lon not in LOCATIONS:
        geolocator = Nominatim(user_agent="WeatherStationInfo-1")
        location = geolocator.reverse("%s, %s" % (lat, lon))
        if not location:
            raise BadLocation
        LOCATIONS[lat_lon] = location.raw
        with open('locations.json', 'w') as jsonfile:
            json.dump(LOCATIONS, jsonfile)
        location = location.raw
    else:
        location = LOCATIONS[lat_lon]
    return location

def modify_load(state, estimated_load, rates):
    prev_rate = rates[0]
    elasticity = elasticity_table[state]
    demand_modifier = 1
    modified_load = []
    for hr, rate in zip(estimated_load, rates):
        delta_rate = ((rate - prev_rate)/prev_rate)
        if delta_rate:
            demand_modifier = 1+delta_rate*elasticity
        prev_rate = rate

        demand = demand_modifier*hr
        if demand < 0:
            demand = 0
        modified_load.append(demand)
    return modified_load

def modify_solar_load(state, estimated_load, generated, rates):
    prev_rate = rates[0]
    elasticity = elasticity_table[state]
    demand_modifier = 1
    modified_load = []
    for hr_load, gen, rate in zip(estimated_load, generated, rates):
        delta_rate = ((rate - prev_rate)/prev_rate)
        if delta_rate:
            demand_modifier = 1+delta_rate*elasticity
        prev_rate = rate

        demand = hr_load
        excess_demand = hr_load - gen
        # if demand is more than system generated reduce grid supplied energy by price
        if excess_demand > 0:
            excess_demand = demand_modifier*excess_demand
            # add back generated energy for SAM's other calculations
            demand = excess_demand + gen
        modified_load.append(demand)
    return modified_load

def modify_battery_load(state, estimated_load, grid_load, rates):
    prev_rate = rates[0]
    elasticity = elasticity_table[state]
    demand_modifier = 1
    modified_load = []
    for hr_load, gl, rate in zip(estimated_load, grid_load, rates):
        delta_rate = ((rate - prev_rate)/prev_rate)
        if delta_rate:
            demand_modifier = 1+delta_rate*elasticity
        prev_rate = rate

        demand = hr_load
        gen = hr_load - gl
        # if grid load is positive, load is met from the grid so reduce grid supplied energy by price
        # grid to load should only be positive or 0
        if gl > 0:
            excess_demand = demand_modifier*gl
            # add back generated energy for SAM's other calculations
            demand = excess_demand + gen
        modified_load.append(demand)
    return modified_load

class BadLocation(Exception):
    pass

class Location():
    loc_id = None
    city = None
    state = None
    resource_file_path = None

    def __repr__(self):
        return "<Location: %s, %s, %s, %s" % (self.loc_id, self.city, self.state, self.resource_file_path)

    def __init__(self, resource_file_path=None):
        self.resource_file_path = resource_file_path
        if not resource_file_path:
            raise BadLocation
        with open(self.resource_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            row = next(reader)
            self.loc_id = row['Location ID']
            self.city = row['City']
            self.state = row['State']
            self.latitude = row['Latitude']
            self.longitude = row['Longitude']
        if not self.state or self.state == "-":
            location = lookup_location(self.latitude , self.longitude)
            if 'state' in location['address']:
                self.state = location['address']['state']
            if 'city' in location['address']:
                self.city = location['address']['city']

def load_location(lon, lat):
    lon_lats = [(lon, lat)]
    location = None
    loc = nsrdbfetcher.fetch(lon_lats)
    for loc in loc.resource_file_paths:
        try:
            location = Location(loc)
        except BadLocation:
            pass
    return location

def load_locations():
    lon_lats = []
    locations = []
    lim = 0
    with open('stations.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #if lim >= 250:
            #    break
            #lon_lats.append((row['longitude'], row['latitude']))
            #lim += 1
            lon_lats = [(row['longitude'], row['latitude'])]
            locs = nsrdbfetcher.fetch(lon_lats)
            for loc in locs.resource_file_paths:
                try:
                    locations.append(Location(loc))
                except BadLocation:
                    pass
    return locations

def datespan(startDate, endDate, delta=timedelta(hours=1)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

def gen_buy_rate_seq(tou_table, ur_ec_tou_mat):
    # 6 columns period, tier, max usage, max usage units, buy, sell
    rates_table = {}
    for rate in ur_ec_tou_mat:
        if rate[0] not in rates_table:
            rates_table[rate[0]] = rate[4]
    rates = []
    for tou in tou_table:
        rates.append(rates_table[tou])
    return rates

def get_rtp_seq():
    rates = []
    with open('columbia_lmp.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # rates are in MWh convert to kWh
            rates.append(float(row['price'])/1000)
    return rates
