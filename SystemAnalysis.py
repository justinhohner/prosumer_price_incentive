import csv, json
import PySAM.Pvwattsv7 as pv
import PySAM.Belpe as ld
import PySAM.Grid as grid
import PySAM.Utilityrate5 as ur
import PySAM.Cashloan as cl
import PySAM.Battwatts as battwatts

from utils import modify_load, modify_solar_load, modify_battery_load, gen_buy_rate_seq, get_rtp_seq

class BaseSystemAnalysis():
    model_name = "PVWattsResidential"
    annual_energy = None
    capital_cost = None
    nominal_lcoe = None
    real_lcoe = None
    npv = None
    full_demand_cost = None
    estimated_load = None

    def __init__(self, location):
        self.location = location
        self.weather_file = self.location.resource_file_path
        # base SAM model
        self.residential_model = pv.default(self.model_name)
        self.load_model = ld.from_existing(self.residential_model, self.model_name)
        self.financial_model = ur.from_existing(self.residential_model, self.model_name)

        self.load_model.LoadProfileEstimator.en_belpe = 1.0
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

    def _get_analysis_output(self, pricing=None):
        return [pricing, self.annual_load, self.capital_cost,
                self.nominal_lcoe, self.real_lcoe, self.npv,
                self.demand_cost]

    def run_static_analysis(self):
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([1.0]*24)]*12)
        self.financial_model.execute(0)
        self.annual_load = round(sum(self.hourly_load_estimate), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        #self.demand_cost = round(self.annual_load * self.location.base_rate, 2)
        self.demand_cost = round(self.financial_model.Outputs.elec_cost_without_system_year1, 2)
        return self._get_analysis_output('Grid static price')

    def run_tou_analysis(self):
        # estimate load due to TOU price increase
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([2.0]*16+[3.0]*5+[2.0]*3)]*12)
        self.financial_model.ur_monthly_fixed_charge = 0
        self.financial_model.execute(0)

        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = gen_buy_rate_seq(tou_table, self.financial_model.ElectricityRates.ur_ec_tou_mat)
        modified_load = modify_load(self.location.state, self.hourly_load_estimate, rates)

        self.annual_load = round(sum(modified_load), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        #self.demand_cost = sum([(ld*rate) for ld, rate in zip(modified_load, rates)])
        #self.demand_cost = round(self.demand_cost, 2)
        self.demand_cost = round(self.financial_model.Outputs.elec_cost_without_system_year1, 2)
        return self._get_analysis_output('Grid TOU price')

    def run_rtp_analysis(self):
        rates = get_rtp_seq()
        modified_load = modify_load(self.location.state, self.hourly_load_estimate, rates)
        assert modified_load != self.hourly_load_estimate

        self.annual_load = round(sum(modified_load), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        # Utilityrate5 does not handle real time pricing
        self.demand_cost = sum([(ld*rate) for ld, rate in zip(modified_load, rates)])
        self.demand_cost = round(self.demand_cost, 2)
        return self._get_analysis_output('Grid RTP price')

class SolarSystemAnalysis(BaseSystemAnalysis):
    model_name = "PVWattsResidential"

    def __init__(self, location):
        BaseSystemAnalysis.__init__(self, location)
        # 10 kW solar system
        # TODO: set class variable for system capacity
        self.residential_model.SystemDesign.system_capacity = 10
        self.residential_model.SolarResource.solar_resource_file = self.weather_file

        #cash_model = cl.from_existing(residential_model, self.model_name)
        self.residential_model.execute(0)
        self.load_model.execute(0)
        self.generated = self.residential_model.Outputs.gen

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
        #self.demand_cost = round(self.financial_model.Outputs.elec_cost_without_system_year1, 2)

        return self._get_analysis_output('Solar static price')

    def run_tou_analysis(self):
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([2.0]*16+[3.0]*5+[2.0]*3)]*12)
        self.financial_model.execute(0)
        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = gen_buy_rate_seq(tou_table, self.financial_model.ElectricityRates.ur_ec_tou_mat)
        modified_load = modify_solar_load(self.location.state, self.hourly_load_estimate, self.generated, rates)

        demand = [(ld-gen) for ld, gen in zip(modified_load, self.generated)]
        self.annual_load = round(sum(demand), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        self.demand_cost = sum([(ld*rate) for ld, rate in zip(modified_load, rates)])
        # financial_model.Outputs.elec_cost_without_system_year1 includes additional fees?
        self.demand_cost = round(self.demand_cost, 2)
        return self._get_analysis_output('Solar TOU price')

    def run_rtp_analysis(self):
        self.financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([2.0]*16+[3.0]*5+[2.0]*3)]*12)
        self.financial_model.execute(0)

        tou_table = self.financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = get_rtp_seq()
        modified_load = modify_solar_load(self.location.state, self.hourly_load_estimate, self.generated, rates)

        demand = [(ld-gen) for ld, gen in zip(modified_load, self.generated)]
        self.annual_load = round(sum(demand), 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        self.demand_cost = sum([(ld*rate) for ld, rate in zip(modified_load, rates)])
        # financial_model.Outputs.elec_cost_without_system_year1 includes additional fees?
        self.demand_cost = round(self.demand_cost, 2)
        return self._get_analysis_output('Solar RTP price')

# taken from https://github.com/NREL/pysam/blob/master/Examples/PySAMWorkshop.ipynb, not sure how accurate
def installed_cost(pv_kw, battery_kw, battery_kwh):
    return pv_kw * 700 + battery_kw * 600 + battery_kwh * 300

class SolarBatterySystemAnalysis(BaseSystemAnalysis):
    model_name = "PVWattsBatteryResidential"
    def __init__(self, location):
        BaseSystemAnalysis.__init__(self, location)
        self.battery_kwh = 15

    def run_static_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        # TODO: set class variable for system capacity
        residential_model.SystemDesign.system_capacity = 10
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

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        # dont trust SAM for this... from grid * rates
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar+Battery static price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost]

    def run_tou_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        # TODO: set class variable for system capacity
        residential_model.SystemDesign.system_capacity = 10
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
                full_demand_cost]

    def run_rtp_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        # TODO: set class variable for system capacity
        residential_model.SystemDesign.system_capacity = 10
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
        rates = get_rtp_seq()
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
                full_demand_cost]
