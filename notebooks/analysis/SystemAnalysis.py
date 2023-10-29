import pandas as pd
from datetime import datetime
import csv, json
import PySAM.Pvwattsv8 as pv
import PySAM.Belpe as ld
import PySAM.Grid as grid
import PySAM.Utilityrate5 as ur
import PySAM.Cashloan as cl
import PySAM.Battwatts as battwatts

from analysis.utils import modify_load, modify_battery_load
from analysis.utils import gen_buy_rate_seq

class BaseSystemAnalysis():
    model_name = "PVWattsResidential"
    system_capacity = 0

    def __init__(self, location):
        self.location = location
        self.weather_file = self.location.resource_file_path
        # base SAM model
        self.residential_model = pv.default(self.model_name)
        self.load_model = ld.from_existing(self.residential_model, self.model_name)
        self.financial_model = ur.from_existing(self.residential_model, self.model_name)

        self.load_model.LoadProfileEstimator.en_belpe = 1.0
        self.load_model.LoadProfileEstimator.en_heat = 0.0
        #self.load_model.LoadProfileEstimator.en_cool = 0.0
        self.financial_model.ur_monthly_fixed_charge = 0
        self.residential_model.SystemDesign.system_capacity = 0
        self.residential_model.SolarResource.solar_resource_file = self.weather_file

        self.residential_model.execute(0)
        self.load_model.execute(0)

        self.hourly_load_estimate = self.load_model.LoadProfileEstimator.load

        # set fixed monthly fees to $0.0
        self.financial_model.ElectricityRates.ur_monthly_fixed_charge = 0.0
        self.financial_model.ElectricityRates.ur_ec_tou_mat = (
            (1.0, 1.0, 1e+38, 0.0, self.location.base_rate, self.location.base_rate),
            (2.0, 1.0, 1e+38, 0.0, self.location.off_peak_rate, self.location.off_peak_rate),
            (3.0, 1.0, 1e+38, 0.0, self.location.off_peak_rate, self.location.off_peak_rate)
        )

    def fixed_rate_demand(self, inc_date=False):
        "return dict of hourly load and prices for fixed rate pricing"
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple(
                [tuple([1.0]*24)]*12
        )
        self.financial_model.execute(0)

        load = self.load_model.LoadProfileEstimator.load
        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        tou_mat = self.financial_model.ElectricityRates.ur_ec_tou_mat
        rates = gen_buy_rate_seq(tou_table, tou_mat)
        demand = {'load':load, 'rate':rates}
        if inc_date:
            startDate = datetime(2019, 1, 1)
            demand['date'] = pd.date_range(startDate, freq='1h', periods=8760)
        return demand

    def tou_demand(self, inc_date=False):
        "return dict of hourly load and prices for time-of-use pricing"
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple(
                [tuple([2.0]*16+[3.0]*5+[2.0]*3)]*12
        )
        self.financial_model.execute(0)

        load = self.load_model.LoadProfileEstimator.load
        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        tou_mat = self.financial_model.ElectricityRates.ur_ec_tou_mat
        rates = gen_buy_rate_seq(tou_table, tou_mat)
        modified_load = modify_load(self.location.state, load, rates)
        demand = {'load':modified_load, 'rate':rates}
        if inc_date:
            startDate = datetime(2019, 1, 1)
            demand['date'] = pd.date_range(startDate, freq='1h', periods=8760)
        return demand

    def rtp_demand(self, inc_date=False):
        "return dict of hourly load and prices for real-time pricing"
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple(
                [tuple([2.0]*16+[3.0]*5+[2.0]*3)]*12
        )
        self.financial_model.execute(0)

        load = self.load_model.LoadProfileEstimator.load
        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        tou_mat = self.financial_model.ElectricityRates.ur_ec_tou_mat
        rates = self.location.get_rtp_seq()
        modified_load = modify_load(self.location.state, load, rates)
        demand = {'load':modified_load, 'rate':rates}
        if inc_date:
            startDate = datetime(2019, 1, 1)
            demand['date'] = pd.date_range(startDate, freq='1h', periods=8760)
        return demand


    def demand(self):
        demand = self.fixed_rate_demand()
        demand['fixed'] = demand.pop('load')
        demand['fixed rate'] = demand.pop('rate')
        startDate = datetime(2019, 1, 1)
        demand['date'] = pd.date_range(startDate, freq='1h', periods=8760)

        tou_demand = self.tou_demand()
        demand['tou'] = tou_demand.pop('load')
        demand['tou rate'] = tou_demand.pop('rate')

        rtp_demand = self.rtp_demand()
        demand['rtp'] = rtp_demand.pop('load')
        demand['rtp rate'] = rtp_demand.pop('rate')

        df = pd.DataFrame.from_dict(demand)
        #df['fixed cost'] = df['fixed'] * demand['fixed rate']
        #df['tou cost'] = df['tou'] * demand['tou rate']
        #df['rtp cost'] = df['rtp'] * demand['rtp rate']
        df['hour'] = df.date.dt.hour
        df['month'] = df.date.dt.month
        return df

    def monthly_bills(self, demand=None):
        if demand is None:
            demand = self.demand()

        demand['fixed cost'] = demand['fixed'] * demand['fixed rate']
        demand['tou cost'] = demand['tou'] * demand['tou rate']
        demand['rtp cost'] = demand['rtp'] * demand['rtp rate']
        return demand

class SolarSystemAnalysis(BaseSystemAnalysis):
    model_name = "PVWattsResidential"
    system_capacity = 10

    def __init__(self, location):
        BaseSystemAnalysis.__init__(self, location)
        # 10 kW solar system
        self.residential_model.SystemDesign.system_capacity = self.system_capacity
        self.residential_model.SolarResource.solar_resource_file = self.weather_file

        #cash_model = cl.from_existing(residential_model, self.model_name)
        self.residential_model.execute(0)
        self.load_model.execute(0)
        self.generated = self.residential_model.Outputs.gen

    def demand(self):
        demand = BaseSystemAnalysis.demand(self)
        demand['generated'] = self.generated
        demand['fixed'] = demand.fixed - demand.generated
        demand['fixed cost'] = demand['fixed'] * demand['fixed rate']
        demand['tou'] = demand.tou - demand.generated
        demand['tou cost'] = demand['tou'] * demand['tou rate']
        demand['rtp'] = demand.rtp - demand.generated
        demand['rtp cost'] = demand['rtp'] * demand['rtp rate']
        return demand

    def run_static_analysis(self):
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([1.0]*24)]*12)
        self.financial_model.execute(0)
        demand = [(ld-gen) for ld, gen in zip(self.hourly_load_estimate, self.generated)]
        self.annual_load = round(sum(demand), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        self.demand_cost = round(sum(demand) * self.location.base_rate, 2)
        return self._get_analysis_output('Solar static price')

# taken from https://github.com/NREL/pysam/blob/master/Examples/PySAMWorkshop.ipynb, not sure how accurate
def installed_cost(pv_kw, battery_kw, battery_kwh):
    return pv_kw * 0 + battery_kw * 0 + battery_kwh * 0

class SolarBatterySystemAnalysis(SolarSystemAnalysis):
    model_name = "PVWattsBatteryResidential"
    system_capacity = 10
    battery_kwh = 13.5

    def __init__(self, location):
        SolarSystemAnalysis.__init__(self, location)

        self.battery_model = battwatts.from_existing(self.residential_model,
                                                     self.model_name)
        self.battery_model.Battery.batt_simple_kwh = self.battery_kwh
        self.battery_model.execute(0)

    def demand(self):
        demand = SolarSystemAnalysis.demand(self)
        demand['generated'] = self.generated
        demand['fixed'] = demand.fixed - demand.generated
        demand['fixed cost'] = demand['fixed'] * demand['fixed rate']
        demand['tou'] = demand.tou - demand.generated
        demand['tou cost'] = demand['tou'] * demand['tou rate']
        demand['rtp'] = demand.rtp - demand.generated
        demand['rtp cost'] = demand['rtp'] * demand['rtp rate']
        demand['grid_power'] = self.battery_model.Outputs.grid_power # Electricity to/from grid [kW]
        demand['grid_to_batt'] = self.battery_model.Outputs.grid_to_batt #Electricity to battery from grid [kW]
        demand['grid_to_load'] = self.battery_model.Outputs.grid_to_load #Electricity to load from grid [kW]
        demand['batt_to_load'] = self.battery_model.Outputs.batt_to_load #Electricity to load from battery [kW]
        return demand

    def run_static_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = self.system_capacity
        residential_model.SolarResource.solar_resource_file = self.weather_file

        grid_model = grid.from_existing(residential_model, self.model_name)
        battery_model = battwatts.from_existing(residential_model, self.model_name)
        battery_model.Battery.batt_simple_kwh = self.battery_kwh
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        grid_model.execute(0)
        battery_model.execute(0)
        financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([1.0]*24)]*12)
        financial_model.execute(0)
        cash_model.total_installed_cost = installed_cost(
                                residential_model.SystemDesign.system_capacity,
                                (self.battery_kwh/4), # 4 hour battery
                                self.battery_kwh)
        cash_model.execute(0)

        grid_power = battery_model.Outputs.grid_power # Electricity to/from grid [kW]
        grid_to_batt = battery_model.Outputs.grid_to_batt #Electricity to battery from grid [kW]
        grid_to_load = battery_model.Outputs.grid_to_load #Electricity to load from grid [kW]
        batt_to_load = battery_model.Outputs.batt_to_load #Electricity to load from battery [kW]
        batt_soc = battery_model.Outputs.batt_SOC

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        # dont trust SAM for this... from grid * rates
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar+Battery static price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost, grid_power, grid_to_batt, grid_to_load, batt_to_load]

    def run_tou_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = self.system_capacity
        residential_model.SolarResource.solar_resource_file = self.weather_file

        grid_model = grid.from_existing(residential_model, self.model_name)
        battery_model = battwatts.from_existing(residential_model, self.model_name)
        battery_model.Battery.batt_simple_kwh = self.battery_kwh
        #battery_model.Battery.batt_dispatch_auto_can_gridcharge = 0.0
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        grid_model.execute(0)
        battery_model.execute(0)
        financial_model.execute(0)
        cash_model.total_installed_cost = installed_cost(
                                residential_model.SystemDesign.system_capacity,
                                (self.battery_kwh/4), # 4 hour battery
                                self.battery_kwh)
        cash_model.execute(0)

        estimated_load = load_model.LoadProfileEstimator.load
        generated = residential_model.Outputs.gen

        grid_power = battery_model.Outputs.grid_power # Electricity to/from grid [kW]
        grid_to_batt = battery_model.Outputs.grid_to_batt #Electricity to battery from grid [kW]
        grid_to_load = battery_model.Outputs.grid_to_load #Electricity to load from grid [kW]
        batt_to_load = battery_model.Outputs.batt_to_load #Electricity to load from battery [kW]
        batt_soc = battery_model.Outputs.batt_SOC

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = gen_buy_rate_seq(tou_table, financial_model.ElectricityRates.ur_ec_tou_mat)
        modified_load = modify_battery_load(self.location.state, estimated_load, grid_to_load, rates)
        load_model.LoadProfileEstimator.load = tuple(modified_load)
        battery_model.execute(0)
        financial_model.execute(0)
        cash_model.execute(0)

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        # dont trust SAM for this... from grid * rates
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar+Battery TOU price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost, grid_power, grid_to_batt, grid_to_load, batt_to_load]

    def run_rtp_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = self.system_capacity
        residential_model.SolarResource.solar_resource_file = self.weather_file

        grid_model = grid.from_existing(residential_model, self.model_name)
        battery_model = battwatts.from_existing(residential_model, self.model_name)
        battery_model.Battery.batt_simple_kwh = self.battery_kwh
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        grid_model.execute(0)
        battery_model.execute(0)
        financial_model.execute(0)
        cash_model.total_installed_cost = installed_cost(
                                residential_model.SystemDesign.system_capacity,
                                (self.battery_kwh/4), # 4 hour battery
                                self.battery_kwh)
        cash_model.execute(0)

        estimated_load = load_model.LoadProfileEstimator.load
        generated = residential_model.Outputs.gen

        grid_power = battery_model.Outputs.grid_power # Electricity to/from grid [kW]
        grid_to_batt = battery_model.Outputs.grid_to_batt #Electricity to battery from grid [kW]
        grid_to_load = battery_model.Outputs.grid_to_load #Electricity to load from grid [kW]
        batt_to_load = battery_model.Outputs.batt_to_load #Electricity to load from battery [kW]
        batt_soc = battery_model.Outputs.batt_SOC

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = self.location.get_rtp_seq()
        modified_load = modify_battery_load(self.location.state, estimated_load, grid_to_load, rates)
        load_model.LoadProfileEstimator.load = tuple(modified_load)
        battery_model.execute(0)
        financial_model.execute(0)
        cash_model.execute(0)

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        # dont trust SAM for this... from grid * rates
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar+Battery RTP price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost, grid_power, grid_to_batt, grid_to_load, batt_to_load]
