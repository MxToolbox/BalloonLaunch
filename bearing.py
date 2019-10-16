# accept command line inputs for lat,lon,alt of target
# read location.txt and output heading and elevation.

import gpsFileWatcher
import argparse
from geographiclib.geodesic import Geodesic

gpsWatcher = gpsFileWatcher

parser = argparse.ArgumentParser(description='Get down range guidance')
parser.add_argument('lat', help="target latitude")
parser.add_argument('lon', help="target longitude")
parser.add_argument('alt', help="target altiture (m)")
args = parser.parse_args()

