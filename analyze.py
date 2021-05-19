#!/usr/bin/env python3

"""
TODO:
    set TOU rates
        single and double peaks
    change tabulated output to json, or something better
    output should include full load data
    output should include peak time analysis
    weather_file vs solar_resource_file? check battery_system.py for example
"""
from tabulate import tabulate

from utils import load_location, elasticity_table
from SystemAnalysis import BaseSystemAnalysis, SolarSystemAnalysis, SolarBatterySystemAnalysis

#How things are – net metering makes consumer indifferent
#	Static price
#	TOU
#	RTP
#locations = load_locations()
locations = [load_location("-92.328594", "38.951551")]
model_name = "PVWattsResidential"
#weather_file = "/Users/justinhohner/SAM Downloaded Weather Files/columbia_mo_38.951551_-92.328594_psm3-tmy_60_tmy.csv"
ran = 0
for location in locations:
    if location.state not in elasticity_table:
        print("skipping %s" % location.state)
        continue
    if ran > 0:
        break
    else:
        ran += 1
    basesystemanalysis = BaseSystemAnalysis(location)
    solarsystemanalysis = SolarSystemAnalysis(location)
    #solarbatterysystemanalysis = SolarBatterySystemAnalysis(location)

    table = []
    table.append(['', 'annual energy', 'capital_cost', 'nominal_lcoe',
                  'real_lcoe', 'npv', 'full_demand_cost'])
    table.append(basesystemanalysis.run_static_analysis())
    table.append(solarsystemanalysis.run_static_analysis())
    #table.append(solarbatterysystemanalysis.run_static_analysis())

    table.append(basesystemanalysis.run_tou_analysis())
    table.append(solarsystemanalysis.run_tou_analysis())
    #table.append(solarbatterysystemanalysis.run_tou_analysis())

    table.append(basesystemanalysis.run_rtp_analysis())
    table.append(solarsystemanalysis.run_rtp_analysis())
    #table.append(solarbatterysystemanalysis.run_rtp_analysis())
    print(tabulate(table))

"""
    # estimate load reduction due to TOU price increase
    estimated_load = load_model.LoadProfileEstimator.load

    tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
    # 6 columns period, tier, max usage, max usage units, buy, sell
    rates_table = {}
    for rate in financial_model.ElectricityRates.ur_ec_tou_mat:
        if rate[0] not in rates_table:
            rates_table[rate[0]] = rate[4]

    #geolocator = Nominatim(user_agent="blargblarg")
    #location = geolocator.reverse("%s, %s" % (residential_model.Outputs.lat, residential_model.Outputs.lon))
    #state = 'Missouri'#location.raw['address']['state']
    #postcode = '65202'#location.raw['address']['postcode']

    modified_load = modify_load(location.state, estimated_load, tou_table, rates_table)
    load_model.LoadProfileEstimator.load = tuple(modified_load)
    financial_model.execute(0)
    #cash_model.execute(0)

    row = ['TOU price']
    row.append(round(sum(modified_load), 2))
    row.append('')#round(cash_model.Outputs.adjusted_installed_cost, 2))
    row.append('')#round(cash_model.Outputs.lcoe_nom, 2))
    row.append('')#round(cash_model.Outputs.lcoe_real, 2))
    row.append('')#round(cash_model.Outputs.npv, 2))
    row.append(round(financial_model.Outputs.elec_cost_without_system_year1, 2))
    table.append(row)"""
    #print(tabulate(table))

"""# estimate load reduction due to RTP price increase
modified_load = []
rate = None

demand_modifier = 1
for hr, tou in zip(estimated_load, tou_table):
    if rate:
        prev_rate = rate
        rate = rates_table[tou]
        delta_rate = ((rate - prev_rate)/prev_rate)
        if delta_rate:
            demand_modifier = 1+delta_rate*elasticity
    else:
        rate = rates_table[tou]
        delta_rate = 0.0

    demand = demand_modifier*hr
    if demand < 0:
        demand = 0
    modified_load.append(demand)

# rerun analysis with elasticity reduced load
load_model.LoadProfileEstimator.load = tuple(modified_load)
financial_model.execute(0)
#cash_model.execute(0)

row = ['RTP price']
row.append(round(sum(modified_load), 2))
row.append('')#round(cash_model.Outputs.adjusted_installed_cost, 2))
row.append('')#round(cash_model.Outputs.lcoe_nom, 2))
row.append('')#round(cash_model.Outputs.lcoe_real, 2))
row.append('')#round(cash_model.Outputs.npv, 2))
row.append(round(financial_model.Outputs.elec_cost_without_system_year1, 2))
table.append(row)"""

#print(tabulate(table))
#generated = load_model.Outputs.gen
