import os
import time
import math
import logging
from datetime import datetime, timedelta 
from gps import *
import threading as thread
import bmp280
import flightModes

gpsd = None 
mode = flightModes
bmp = bmp280



def pressureAltitude(millibars):
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    return round(((1 - (millibars / 1013.25)** 0.190284)) * 145366.45, 0)

maxAltPressure = 0 # feet
maxAltGps = 0  # meters
lastPressureAlt = pressureAltitude(bmp.sensor.pressure)
lastGoodGpsFix = datetime.now()
lastGoodLat = math.nan
lastGoodLon = math.nan
lastGoodAlt = math.nan

# GPS monitoring Thread:
#----------------------------------------------
def refreshGpsd():
    global gpsd
    while True:
        gpsd.next()
        time.sleep(.1)  
    
logging.info('Iniitializing GPSD...')
print("Iniitializing GPSD...")
gpsd = gps(mode=WATCH_ENABLE) 
tracker_thread=thread.Thread(target=refreshGpsd) 
tracker_thread.setDaemon(True)                  
tracker_thread.start()  