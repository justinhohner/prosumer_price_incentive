#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

from analysis.SystemAnalysis import BaseSystemAnalysis, SolarSystemAnalysis
from analysis.utils import load_locations
from analysis.utils import modify_load, modify_battery_load
from analysis.utils import gen_buy_rate_seq, get_rtp_seq

def annual_graph(demand, location, k, y_min, y_max, show=False):
    demand.plot(y=k, x='date')
    plt.ylim(y_min, y_max)
    plt.grid()
    plt.axis()
    title = "%s - Annual %s" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def hourly_graph(demand, location, k, y_min, y_max, show=False):
    demand.plot(y=k, x='hour', kind='scatter')
    plt.ylim(y_min, y_max)
    plt.grid()
    plt.axis()
    title = "%s - Hourly %s" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def annual_solar_graph(demand, location, k, y_min, y_max, show=False):
    demand.plot(y=k, x='date')
    plt.ylim(y_min, y_max)
    plt.grid()
    plt.axis()
    title = "%s - Annual Solar %s" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def hourly_solar_graph(demand, location, k, y_min, y_max, show=False):
    demand.plot(y=k, x='hour', kind='scatter')
    plt.ylim(y_min, y_max)
    plt.grid()
    plt.axis()
    title = "%s - Hourly Solar %s" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def bill_hist(demand, location, k, show=False):
    bill = "%s cost" % k
    demand.groupby(['month']).sum()[bill].hist()
    title = "%s - %s Monthly Bill" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def solar_bill_hist(demand, location, k, show=False):
    bill = "%s cost" % k
    demand.groupby(['month']).sum()[bill].hist()
    title = "%s - %s Solar Monthly Bill" % (location.state, k.title())
    plt.title(title)
    if show:
        plt.show()
    else:
        plt.savefig('%s.png' % title)
    plt.close()

def analyze(location, show=False):
    bsa = BaseSystemAnalysis(location)
    ssa = SolarSystemAnalysis(location)

    demand = bsa.demand()
    solar_demand = ssa.demand()
    y_min = 0
    y_max = 0
    for k in ['fixed', 'tou', 'rtp']:
        y_min = min(y_min, min(solar_demand[k]), min(demand[k]))
        y_max = max(y_max, max(solar_demand[k]), max(demand[k]))

    for k in ['fixed', 'tou', 'rtp']:
        #print(demand[k].describe())
        #print(solar_demand[k].describe())
        bill_hist(demand, location, k, show)
        annual_graph(demand, location, k, y_min, y_max, show)
        hourly_graph(demand, location, k, y_min, y_max, show)

        solar_bill_hist(solar_demand, location, k, show)
        annual_solar_graph(solar_demand, location, k, y_min, y_max, show)
        hourly_solar_graph(solar_demand, location, k, y_min, y_max, show)

if __name__ == "__main__":
    locations = load_locations()
    #location = locations[0]
    for location in locations:
        if location.state == "-":
            continue
        if location.state == 'Puerto Rico':
            continue
        #print(location)
        analyze(location)
