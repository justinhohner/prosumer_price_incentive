#!/usr/bin/env python3

# https://www.weather.gov/documentation/services-web-api
# https://w1.weather.gov/xml/current_obs/index.xml
# https://w1.weather.gov/xml/current_obs/
import csv
import requests
import xml.etree.ElementTree as ET

xmlfile = 'index.xml'
tree = ET.parse(xmlfile)
root = tree.getroot()

fieldnames = []
stations = []
for station in root.findall('./station'):
    row = {}
    #for elem in station.getchildren():
    for elem in list(station):
        if elem.tag not in row:
            row[elem.tag] = elem.text
        if elem.tag not in fieldnames:
            fieldnames.append(elem.tag)
    stations.append(row)


#print(stations)
with open('stations.csv', 'w') as csvfile:
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csvwriter.writeheader()
    csvwriter.writerows(stations)

