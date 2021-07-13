#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

from analysis.SystemAnalysis import BaseSystemAnalysis, SolarSystemAnalysis, SolarBatterySystemAnalysis
from analysis.utils import load_locations
from analysis.utils import modify_load, modify_battery_load
from analysis.utils import gen_buy_rate_seq

def annual_graph(demand, k, y_min, y_max, title, show=False):
    demand.plot(y=k, x='date')
    plt.ylim(y_min, y_max)
    plt.grid()
    plt.axis()
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def hourly_graph(demand, k, title, show=False):
    demand.boxplot(column=k, by='hour', whis=(0,100))
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('output/load/%s.png' % title)
    plt.close()

def monthly_bill_lines(demand, title, show=False):
    for k in ['fixed', 'tou', 'rtp']:
        bill = "%s cost" % k
        plt.plot(demand.groupby(['month']).sum()[bill], label=k.title())
    plt.title(title)
    plt.legend()
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def monthly_bill_hist(demand, bill, title, show=False):
    demand.groupby(['month']).sum()[bill].hist()
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def analyze(location, show=False):
    bsa = BaseSystemAnalysis(location)
    ssa = SolarSystemAnalysis(location)
    sbsa = SolarBatterySystemAnalysis(location)

    demand = bsa.demand()
    solar_demand = ssa.demand()
    battery_demand = sbsa.demand()
    y_min = 0
    y_max = 0
    for k in ['fixed', 'tou', 'rtp']:
        y_min = min(y_min, min(solar_demand[k]), min(demand[k]))
        y_max = max(y_max, max(solar_demand[k]), max(demand[k]))

    location_info = "%s, %s (%s)" % (location.city, location.state,
                                     location.iso)
    #title = "%s - Grid Monthly Bills" % location_info
    #monthly_bill_lines(demand, title)
    #title = "%s - Solar Monthly Bills" % location_info
    #monthly_bill_lines(solar_demand, title)
    #title = "%s - Solar+Battery Monthly Bills" % location_info
    #monthly_bill_lines(battery_demand, title)

    ############# one big chart ###############
    title = "%s - Monthly Bills" % location_info

    plt.plot(demand.groupby(['month']).sum()['fixed cost'],
             label='Grid Fixed Cost', color='tab:blue', linestyle='solid')
    plt.plot(solar_demand.groupby(['month']).sum()['fixed cost'],
             label='Solar Fixed Cost', color='tab:blue', linestyle='dotted')
    plt.plot(battery_demand.groupby(['month']).sum()['fixed cost'],
             label='Solar+Battery Fixed Cost', color='tab:blue', linestyle='dashed')

    plt.plot(demand.groupby(['month']).sum()['tou cost'],
             label='Grid TOU Cost', color='tab:orange', linestyle='solid')
    plt.plot(solar_demand.groupby(['month']).sum()['tou cost'],
             label='Solar TOU Cost', color='tab:orange', linestyle='dotted')
    plt.plot(battery_demand.groupby(['month']).sum()['tou cost'],
             label='Solar+Battery TOU Cost', color='tab:orange', linestyle='dashed')

    plt.plot(demand.groupby(['month']).sum()['rtp cost'],
             label='Grid RTP Cost', color='tab:green', linestyle='solid')
    plt.plot(solar_demand.groupby(['month']).sum()['rtp cost'],
             label='Solar RTP Cost', color='tab:green', linestyle='dotted')
    plt.plot(battery_demand.groupby(['month']).sum()['rtp cost'],
             label='Solar+Battery RTP Cost', color='tab:green', linestyle='dashed')

    plt.title(title)
    plt.legend()
    plt.savefig('%s.png' % title)
    plt.close()
    ################################
    for k in ['fixed', 'tou', 'rtp']:
        #print(demand[k].describe())
        #print(solar_demand[k].describe())

        bill = "%s cost" % k
        title = "%s - %s Monthly Bill" % (location.state, k.title())
        #monthly_bill_hist(demand, bill, title, show)
        title = "%s - Annual %s" % (location.state, k.title())
        #annual_graph(demand, k, y_min, y_max, title, show)
        title = "%s - Hourly %s" % (location_info, k.title())
        hourly_graph(demand, k, title, show)

        title = "%s - %s Monthly Solar Bill" % (location.state, k.title())
        #monthly_bill_hist(solar_demand, bill, title, show)
        title = "%s - Annual Solar %s" % (location.state, k.title())
        #annual_graph(solar_demand, k, y_min, y_max, title, show)
        title = "%s - Hourly Solar %s" % (location_info, k.title())
        hourly_graph(solar_demand, k, title, show)

        title = "%s - %s Monthly Solar+Battery Bill" % (location.state, k.title())
        #monthly_bill_hist(battery_demand, bill, title, show)
        title = "%s - Annual Solar+Battery %s" % (location.state, k.title())
        #annual_graph(battery_demand, k, y_min, y_max, title, show)
        title = "%s - Hourly Solar+Battery %s" % (location_info, k.title())
        hourly_graph(battery_demand, k, title, show)

if __name__ == "__main__":
    locations = load_locations()
    for location in locations:
        analyze(location)


#monthly_demand = demand.groupby(['month']).sum()[['fixed cost', 'tou cost', 'rtp cost']].add_prefix('grid ')
#monthly_demand = monthly_demand.merge(solar_demand.groupby(['month']).sum()[['fixed cost', 'tou cost', 'rtp cost']].add_prefix('solar '),
#                     on='month')
#monthly_demand = monthly_demand.merge(battery_demand.groupby(['month']).sum()[['fixed cost', 'tou cost', 'rtp cost']].add_prefix('solar+batt '),
#                     on='month')
#monthly_demand.plot()
