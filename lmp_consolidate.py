#!/usr/bin/env python3
import os
import csv
from datetime import datetime
from utils import datespan

days = []
for root, dirs, files in os.walk("rt_lmp"):
   for name in files:
      year = int(name[0:4])
      month = int(name[4:6])
      day = int(name[6:8])
      with open(os.path.join(root, name), 'r') as csvfile:
          reader = csv.reader(csvfile)
          for row in reader:
              if len(row) < 3:
                  next
              elif (row[0] == "AMMO.UE" and row[1] == "Loadzone" and row[2] == "LMP"):
                  for hr, price in enumerate(row[3:]):
                      days.append({'dt': datetime(year, month, day, hr), 'price': price})
                  break
      #print(os.path.join(root, name))
      #print("%s, %s, %s" %(year, month, day))
      #print(datetime(year, month, day))

newlist = sorted(days, key=lambda k: k['dt']) 
with open('columbia_lmp.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['dt', 'price'])
    writer.writeheader()
    writer.writerows(newlist)
'''
base_fname = 'rt_lmp/{year}{month:02}{day:02}_rt_lmp_final.csv'

startDate = datetime(2019, 1, 1)
endDate = datetime(2020, 1, 1)
for dt in datespan(startDate, endDate, delta=timedelta(days=1)):
    lmp_file = base_fname.format(year=dt.year, month=dt.month, day=dt.day)
    lmp_url = base_url.format(year=dt.year, month=dt.month, day=dt.day)
    resp = requests.get(lmp_url)
    with open(lmp_file, 'wb') as localfile:
        localfile.write(resp.content)
    sleep(2)


AMMO.UE	Loadzone	LMP
'''
