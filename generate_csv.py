#!/usr/bin/env python3.8

import pandas as pd
import matplotlib.pyplot as plt

from analysis.SystemAnalysis import BaseSystemAnalysis, SolarSystemAnalysis, SolarBatterySystemAnalysis
from analysis.utils import load_locations
from analysis.utils import modify_load, modify_battery_load
from analysis.utils import gen_buy_rate_seq

def generate(location, show=False):
    bsa = BaseSystemAnalysis(location)
    ssa = SolarSystemAnalysis(location)
    sbsa = SolarBatterySystemAnalysis(location)

    demand = bsa.demand()
    solar_demand = ssa.demand()
    battery_demand = sbsa.demand()

    location_info = "%s, %s (%s)" % (location.city, location.state,
                                     location.iso)
    fname = f"unscaled-{location_info}-bsa.csv"
    demand.to_csv(fname)

    fname = f"unscaled-{location_info}-ssa.csv"
    solar_demand.to_csv(fname)

    fname = f"unscaled-{location_info}-sbsa.csv"
    battery_demand.to_csv(fname)

if __name__ == "__main__":
    locations = load_locations()
    for location in locations:
        generate(location)

