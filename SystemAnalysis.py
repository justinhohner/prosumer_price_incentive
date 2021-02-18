import csv
import PySAM.Pvwattsv7 as pv
import PySAM.Belpe as ld
import PySAM.Grid as grid
import PySAM.Utilityrate5 as ur
import PySAM.Cashloan as cl
import PySAM.Battwatts as battwatts

from utils import modify_load, modify_solar_load, modify_battery_load, gen_buy_rate_seq, get_rtp_seq

class SystemAnalysis():
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

    def run_static_analysis(self):
        # base SAM model
        residential_model = pv.default(self.model_name)
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.SystemDesign.system_capacity = 0
        residential_model.SolarResource.solar_resource_file = self.weather_file

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([1.0]*24)]*12)
        financial_model.execute(0)
        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule

        self.annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        self.full_demand_cost = round(financial_model.Outputs.elec_cost_without_system_year1, 2)
        return self._get_analysis_output('Grid static price')

    def _get_analysis_output(self, pricing=None):
        return [pricing, self.annual_energy, self.capital_cost,
                self.nominal_lcoe, self.real_lcoe, self.npv,
                self.full_demand_cost]

    def run_tou_analysis(self):
        # estimate load reduction due to TOU price increase
        residential_model = pv.default(self.model_name)
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.SystemDesign.system_capacity = 0
        residential_model.SolarResource.solar_resource_file = self.weather_file

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.execute(0)
        estimated_load = load_model.LoadProfileEstimator.load

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = gen_buy_rate_seq(tou_table, financial_model.ElectricityRates.ur_ec_tou_mat)
        modified_load = modify_load(self.location.state, estimated_load, rates)
        load_model.LoadProfileEstimator.load = tuple(modified_load)
        financial_model.execute(0)
        self.annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        self.full_demand_cost = round(financial_model.Outputs.elec_cost_without_system_year1, 2)
        return self._get_analysis_output('Grid TOU price')

    def run_rtp_analysis(self):
        residential_model = pv.default(self.model_name)
        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.SystemDesign.system_capacity = 0
        residential_model.SolarResource.solar_resource_file = self.weather_file

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.execute(0)
        estimated_load = load_model.LoadProfileEstimator.load

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = get_rtp_seq()
        modified_load = modify_load(self.location.state, estimated_load, rates)

        load_model.LoadProfileEstimator.load = tuple(modified_load)
        financial_model.execute(0)
        self.annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        self.capital_cost = None
        self.nominal_lcoe = None
        self.real_lcoe = None
        self.npv = None
        #self.full_demand_cost = round(financial_model.Outputs.annual_energy_value, 2)
        self.full_demand_cost = round(financial_model.Outputs.elec_cost_without_system_year1, 2)
        return self._get_analysis_output('Grid RTP price')

class SolarSystemAnalysis():
    model_name = "PVWattsResidential"

    def __init__(self, location):
        SystemAnalysis.__init__(self, location)

    def run_static_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = 10
        residential_model.SolarResource.solar_resource_file = self.weather_file

        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.ElectricityRates.ur_ec_sched_weekday = tuple([tuple([1.0]*24)]*12)
        financial_model.execute(0)
        cash_model.execute(0)

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar static price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost]

    def run_tou_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = 10
        residential_model.SolarResource.solar_resource_file = self.weather_file

        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.execute(0)

        # estimate load reduction due to TOU price increase
        estimated_load = load_model.LoadProfileEstimator.load
        generated = residential_model.Outputs.gen

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = gen_buy_rate_seq(tou_table, financial_model.ElectricityRates.ur_ec_tou_mat)
        modified_load = modify_solar_load(self.location.state, estimated_load, generated, rates)
        load_model.LoadProfileEstimator.load = tuple(modified_load)
        load_model.execute(0)
        financial_model.execute(0)
        cash_model.execute(0)

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar TOU price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost]

    def run_rtp_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
        residential_model.SystemDesign.system_capacity = 10
        residential_model.SolarResource.solar_resource_file = self.weather_file

        load_model = ld.from_existing(residential_model, self.model_name)
        financial_model = ur.from_existing(residential_model, self.model_name)
        cash_model = cl.from_existing(residential_model, self.model_name)

        residential_model.execute(0)
        load_model.execute(0)
        financial_model.execute(0)

        # estimate load reduction due to TOU price increase
        estimated_load = load_model.LoadProfileEstimator.load
        generated = residential_model.Outputs.gen

        tou_table = financial_model.Outputs.year1_hourly_ec_tou_schedule
        rates = get_rtp_seq()
        modified_load = modify_solar_load(self.location.state, estimated_load, generated, rates)
        load_model.LoadProfileEstimator.load = tuple(modified_load)
        load_model.execute(0)
        financial_model.execute(0)
        cash_model.execute(0)

        annual_energy = round(financial_model.Outputs.annual_electric_load[1], 2)
        capital_cost = round(cash_model.Outputs.adjusted_installed_cost, 2)
        nominal_lcoe = round(cash_model.Outputs.lcoe_nom, 2)
        real_lcoe = round(cash_model.Outputs.lcoe_real, 2)
        npv = round(cash_model.Outputs.npv, 2)
        full_demand_cost = round(financial_model.Outputs.elec_cost_with_system_year1, 2)
        return ['Solar RTP price', annual_energy, capital_cost,
                nominal_lcoe, real_lcoe, npv,
                full_demand_cost]

# taken from https://github.com/NREL/pysam/blob/master/Examples/PySAMWorkshop.ipynb, not sure how accurate
def installed_cost(pv_kw, battery_kw, battery_kwh):
    return pv_kw * 700 + battery_kw * 600 + battery_kwh * 300

class SolarBatterySystemAnalysis(SystemAnalysis):
    model_name = "PVWattsBatteryResidential"
    def __init__(self, location):
        SystemAnalysis.__init__(self, location)
        self.battery_kwh = 15

    def run_static_analysis(self):
        residential_model = pv.default(self.model_name)
        # 10 kW solar system
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
