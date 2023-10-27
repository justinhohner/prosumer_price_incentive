
import os
import csv
import requests
from contextlib import closing
import json
from datetime import date, datetime, timedelta
from time import sleep

from geopy.geocoders import Nominatim

import urllib3
urllib3.disable_warnings()

import analysis.ResourceTools as tools

#https://github.com/NREL/pysam/blob/master/Examples/FetchResourceFileExample.py
nrel_api_key = os.getenv("NREL_API_KEY")
nrel_api_email = os.getenv("NREL_API_EMAIL")
nsrdbfetcher = tools.FetchResourceFiles(
                tech='solar',
                nrel_api_key=nrel_api_key,
                nrel_api_email=nrel_api_email)


elasticity_table = {}
regional_elasticities = {}
electricity_rates = {}
# TODO move files and create functions
with open('data/short-run price elasticities for the residential electricity market.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        regional_elasticities[row['Division']] = float(row['elasticity'])

with open('data/us census bureau regions and divisions.csv') as csvfile:
    #State,State Code,Region,Division
    reader = csv.DictReader(csvfile)
    for row in reader:
        elasticity_table[row['State']] = regional_elasticities[row['Division']]

with open('data/us electricity rates.csv') as csvfile:
    # https://www.eia.gov/electricity/state/
    #'Name', 'Average retail price (cents/kWh)', 'Net summer capacity (MW)', 'Net generation (MWh)', 'Total retail sales (MWh)'
    reader = csv.DictReader(csvfile)
    for row in reader:
        # convert cents per kWh to dollars per kWh
        electricity_rates[row['Name']] = float(row['Average retail price (cents/kWh)'])/100

try:
    with open('data/locations.json', 'r') as jsonfile:
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
        pct_change = ((rate - prev_rate)/prev_rate)
        if pct_change:
            demand_modifier = 1+pct_change*elasticity
        prev_rate = rate

        demand = demand_modifier*hr
        if demand < 0:
            demand = 0
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

class BadLocationResponse(Exception):
    pass

class BadLocation(Exception):
    pass

class Location():
    loc_id = None
    iso = None
    city = None
    state = None
    resource_file_path = None
    base_rate = 0.0
    peak_rate = 0.0
    off_peak_rate = 0.0

    def __repr__(self):
        return "<Location: %s, %s, %s, %s, %s" % (self.loc_id, self.iso,
                                                  self.city, self.state,
                                                  self.resource_file_path)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'iso':
                self.iso = value
            if key == 'resource_file_path':
                self.resource_file_path = value
        if not self.resource_file_path:
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
        if self.state in electricity_rates:
            self.base_rate = electricity_rates[self.state]
            self.peak_rate = 1.5*self.base_rate
            self.off_peak_rate = 0.5*self.base_rate

    def get_rtp_seq(self):
        rates = []
        fname = "data/rates/%s, %s/%s/prices.csv" % (self.city,
                                                     self.state,
                                                     self.iso.upper())
        with open(fname, 'r') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                for k in row.keys():
                    if k.startswith("HE "):
                        # mW to kW
                        r = (float(row[k])/1000)
                        rates.append(r)
        return rates

def load_locations():
    lon_lats = []
    locations = []
    #'https://www2.census.gov/geo/docs/reference/cenpop2010/CenPop2010_Mean_ST.txt'
    with open('data/locations.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lon_lats = [(row['LONGITUDE'], row['LATITUDE'])]
            locs = nsrdbfetcher.fetch(lon_lats)
            sleep(2)
            for loc in locs.resource_file_paths:
                try:
                    locations.append(Location(resource_file_path=loc, iso=row['ISO']))
                except BadLocation:
                    pass
    return locations

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
