#!/usr/bin/env python3
import requests
from time import sleep
from datetime import datetime, timedelta
from utils import datespan
base_url = 'https://docs.misoenergy.org/marketreports/{year}{month:02}{day:02}_rt_lmp_final.csv'
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
