# accept command line inputs for lat,lon,alt of target
# read location.txt and output heading and elevation.
# IMPORTANT:  winlocation.ps1 should be running (or you can manually edit the location.txt file with the local position)

import math
import numpy
import gpsFileWatcher
import argparse
from geographiclib.geodesic import Geodesic

localGps = gpsFileWatcher

parser = argparse.ArgumentParser(description='Get down range guidance')
parser.add_argument('lat', help="target latitude")
parser.add_argument('lon', help="target longitude")
parser.add_argument('alt', help="target altiture (m)")
args = parser.parse_args()

geo = Geodesic.WGS84.Inverse(localGps.latitude, localGps.longitude, float(args.lat), float(args.lon))
distance = int(geo['s12'])
azimuth = int(geo['azi1'])
azi1=azimuth
if azimuth < 0:
    azimuth = 360 + azimuth


elevation = 0
los_range = 0
if distance > 0:
    altDeltaMeters = float(args.alt) - localGps.altitude  # meters
    print(altDeltaMeters)
    elevation = str(int((numpy.arctan(altDeltaMeters / distance)) * 57.2958))  #radians to degrees
    los_range = math.sqrt(altDeltaMeters**2 + distance**2)


formatStr = '| {0:>17} | {1:<26} |'
print('________________________________________________')
print(formatStr.format("Local Lat", round(localGps.latitude, 6)))
print(formatStr.format("Local Lon",  round(localGps.longitude, 6)))
print(formatStr.format("Local Alt (m)", localGps.altitude))
print(formatStr.format("LOS Range (m)", int(los_range)))
print(formatStr.format("Down Range (m)", distance))
print(formatStr.format("Heading", azimuth))
print(formatStr.format("Elevation", elevation))

print('________________________________________________')
