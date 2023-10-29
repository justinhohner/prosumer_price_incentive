import pandas as pd

fname = "unscaled-Downtown Kansas City, Missouri (SPP)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['KC, MO (SPP) Grid Fixed'] = base_df.pop('fixed')
base_df['KC, MO (SPP) Fixed Rate'] = base_df.pop('fixed rate')
base_df['KC, MO (SPP) Grid TOU'] = base_df.pop('tou')
base_df['KC, MO (SPP) TOU Rate'] = base_df.pop('tou rate')
base_df['KC, MO (SPP) Grid RTP'] = base_df.pop('rtp')
base_df['KC, MO (SPP) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Downtown Kansas City, Missouri (SPP)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['KC, MO (SPP) Solar Fixed'] = solar_df.pop('fixed')
base_df['KC, MO (SPP) Solar TOU'] = solar_df.pop('tou')
base_df['KC, MO (SPP) Solar RTP'] = solar_df.pop('rtp')
base_df['KC, MO (SPP) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Downtown Kansas City, Missouri (SPP)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['KC, MO (SPP) Battery Fixed'] = battery_df.pop('fixed')
base_df['KC, MO (SPP) Battery TOU'] = battery_df.pop('tou')
base_df['KC, MO (SPP) Battery RTP'] = battery_df.pop('rtp')
base_df['KC, MO (SPP) Battery Generated'] = battery_df.pop('generated')
base_df['KC, MO (SPP) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['KC, MO (SPP) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['KC, MO (SPP) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['KC, MO (SPP) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('KC, MO (SPP).csv')

###############################

fname = "unscaled-Fargo, North Dakota (MISO)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['Fargo, ND (MISO) Grid Fixed'] = base_df.pop('fixed')
base_df['Fargo, ND (MISO) Fixed Rate'] = base_df.pop('fixed rate')
base_df['Fargo, ND (MISO) Grid TOU'] = base_df.pop('tou')
base_df['Fargo, ND (MISO) TOU Rate'] = base_df.pop('tou rate')
base_df['Fargo, ND (MISO) Grid RTP'] = base_df.pop('rtp')
base_df['Fargo, ND (MISO) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Fargo, North Dakota (MISO)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['Fargo, ND (MISO) Solar Fixed'] = solar_df.pop('fixed')
base_df['Fargo, ND (MISO) Solar TOU'] = solar_df.pop('tou')
base_df['Fargo, ND (MISO) Solar RTP'] = solar_df.pop('rtp')
base_df['Fargo, ND (MISO) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Fargo, North Dakota (MISO)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['Fargo, ND (MISO) Battery Fixed'] = battery_df.pop('fixed')
base_df['Fargo, ND (MISO) Battery TOU'] = battery_df.pop('tou')
base_df['Fargo, ND (MISO) Battery RTP'] = battery_df.pop('rtp')
base_df['Fargo, ND (MISO) Battery Generated'] = battery_df.pop('generated')
base_df['Fargo, ND (MISO) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['Fargo, ND (MISO) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['Fargo, ND (MISO) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['Fargo, ND (MISO) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('Fargo, ND (MISO).csv')

##################################################

fname = "unscaled-Fargo, North Dakota (SPP)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['Fargo, ND (SPP) Grid Fixed'] = base_df.pop('fixed')
base_df['Fargo, ND (SPP) Fixed Rate'] = base_df.pop('fixed rate')
base_df['Fargo, ND (SPP) Grid TOU'] = base_df.pop('tou')
base_df['Fargo, ND (SPP) TOU Rate'] = base_df.pop('tou rate')
base_df['Fargo, ND (SPP) Grid RTP'] = base_df.pop('rtp')
base_df['Fargo, ND (SPP) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Fargo, North Dakota (SPP)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['Fargo, ND (SPP) Solar Fixed'] = solar_df.pop('fixed')
base_df['Fargo, ND (SPP) Solar TOU'] = solar_df.pop('tou')
base_df['Fargo, ND (SPP) Solar RTP'] = solar_df.pop('rtp')
base_df['Fargo, ND (SPP) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Fargo, North Dakota (SPP)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['Fargo, ND (SPP) Battery Fixed'] = battery_df.pop('fixed')
base_df['Fargo, ND (SPP) Battery TOU'] = battery_df.pop('tou')
base_df['Fargo, ND (SPP) Battery RTP'] = battery_df.pop('rtp')
base_df['Fargo, ND (SPP) Battery Generated'] = battery_df.pop('generated')
base_df['Fargo, ND (SPP) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['Fargo, ND (SPP) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['Fargo, ND (SPP) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['Fargo, ND (SPP) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('Fargo, ND (SPP).csv')

##################################################
fname = "unscaled-Houston, Texas (ERCOT)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['Houston, TX (ERCOT) Grid Fixed'] = base_df.pop('fixed')
base_df['Houston, TX (ERCOT) Fixed Rate'] = base_df.pop('fixed rate')
base_df['Houston, TX (ERCOT) Grid TOU'] = base_df.pop('tou')
base_df['Houston, TX (ERCOT) TOU Rate'] = base_df.pop('tou rate')
base_df['Houston, TX (ERCOT) Grid RTP'] = base_df.pop('rtp')
base_df['Houston, TX (ERCOT) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Houston, Texas (ERCOT)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['Houston, TX (ERCOT) Solar Fixed'] = solar_df.pop('fixed')
base_df['Houston, TX (ERCOT) Solar TOU'] = solar_df.pop('tou')
base_df['Houston, TX (ERCOT) Solar RTP'] = solar_df.pop('rtp')
base_df['Houston, TX (ERCOT) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Houston, Texas (ERCOT)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['Houston, TX (ERCOT) Battery Fixed'] = battery_df.pop('fixed')
base_df['Houston, TX (ERCOT) Battery TOU'] = battery_df.pop('tou')
base_df['Houston, TX (ERCOT) Battery RTP'] = battery_df.pop('rtp')
base_df['Houston, TX (ERCOT) Battery Generated'] = battery_df.pop('generated')
base_df['Houston, TX (ERCOT) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['Houston, TX (ERCOT) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['Houston, TX (ERCOT) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['Houston, TX (ERCOT) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('Houston, TX (ERCOT).csv')

##################################################
fname = "unscaled-Houston, Texas (MISO)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['Houston, TX (MISO) Grid Fixed'] = base_df.pop('fixed')
base_df['Houston, TX (MISO) Fixed Rate'] = base_df.pop('fixed rate')
base_df['Houston, TX (MISO) Grid TOU'] = base_df.pop('tou')
base_df['Houston, TX (MISO) TOU Rate'] = base_df.pop('tou rate')
base_df['Houston, TX (MISO) Grid RTP'] = base_df.pop('rtp')
base_df['Houston, TX (MISO) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Houston, Texas (MISO)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['Houston, TX (MISO) Solar Fixed'] = solar_df.pop('fixed')
base_df['Houston, TX (MISO) Solar TOU'] = solar_df.pop('tou')
base_df['Houston, TX (MISO) Solar RTP'] = solar_df.pop('rtp')
base_df['Houston, TX (MISO) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Houston, Texas (MISO)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['Houston, TX (MISO) Battery Fixed'] = battery_df.pop('fixed')
base_df['Houston, TX (MISO) Battery TOU'] = battery_df.pop('tou')
base_df['Houston, TX (MISO) Battery RTP'] = battery_df.pop('rtp')
base_df['Houston, TX (MISO) Battery Generated'] = battery_df.pop('generated')
base_df['Houston, TX (MISO) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['Houston, TX (MISO) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['Houston, TX (MISO) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['Houston, TX (MISO) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('Houston, TX (MISO).csv')

##################################################
fname = "unscaled-Saint Louis, Missouri (MISO)-bsa.csv"
base_df = pd.read_csv(fname)

base_df['STL, MO (MISO) Grid Fixed'] = base_df.pop('fixed')
base_df['STL, MO (MISO) Fixed Rate'] = base_df.pop('fixed rate')
base_df['STL, MO (MISO) Grid TOU'] = base_df.pop('tou')
base_df['STL, MO (MISO) TOU Rate'] = base_df.pop('tou rate')
base_df['STL, MO (MISO) Grid RTP'] = base_df.pop('rtp')
base_df['STL, MO (MISO) RTP Rate'] = base_df.pop('rtp rate')

fname = "unscaled-Saint Louis, Missouri (MISO)-ssa.csv"
solar_df = pd.read_csv(fname)
base_df['STL, MO (MISO) Solar Fixed'] = solar_df.pop('fixed')
base_df['STL, MO (MISO) Solar TOU'] = solar_df.pop('tou')
base_df['STL, MO (MISO) Solar RTP'] = solar_df.pop('rtp')
base_df['STL, MO (MISO) Solar Generated'] = solar_df.pop('generated')

fname = "unscaled-Saint Louis, Missouri (MISO)-sbsa.csv"
battery_df = pd.read_csv(fname)
base_df['STL, MO (MISO) Battery Fixed'] = battery_df.pop('fixed')
base_df['STL, MO (MISO) Battery TOU'] = battery_df.pop('tou')
base_df['STL, MO (MISO) Battery RTP'] = battery_df.pop('rtp')
base_df['STL, MO (MISO) Battery Generated'] = battery_df.pop('generated')
base_df['STL, MO (MISO) Battery Grid Power'] = battery_df.pop('grid_power')
base_df['STL, MO (MISO) Battery Grid to battery'] = battery_df.pop('grid_to_batt')
base_df['STL, MO (MISO) Battery Grid to Load'] = battery_df.pop('grid_to_load')
base_df['STL, MO (MISO) Battery Battery to Load'] = battery_df.pop('batt_to_load')

base_df.to_csv('STL, MO (SPP).csv')

