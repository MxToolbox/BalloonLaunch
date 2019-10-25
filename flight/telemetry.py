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

maxAltPressure = 0 # feet
maxAltGps = 0  # meters
verticalSpeedFps = 0

lastTemperature  = 0
lastPressure = 0
lastPressureAlt = 0
lastGoodGpsFix = datetime.now()
lastGoodLat = math.nan
lastGoodLon = math.nan
lastGoodAlt = math.nan

def update():
    global lastGoodLat
    global lastGoodLon 
    global lastGoodAlt 
    global lastGoodGpsFix 
    global lastTemperature
    currentLat = gpsd.fix.latitude
    currentLon = gpsd.fix.longitude
    currentAlt = gpsd.fix.altitude
    if math.isnan(currentLat) or math.isnan(currentLon) or math.isnan(currentAlt):
        mode.hasGpsFix = False
    else:
        mode.hasGpsFix = True
        lastGoodLat = currentLat
        lastGoodLon = currentLon
        lastGoodAlt = currentAlt
        lastGoodGpsFix = datetime.now()    
        # Check Max GPS Alt
        if lastGoodAlt > maxAltGps:
            maxAltGps = lastGoodAlt 
    
    # Update pressure Alt
    pressureAltitude()
    lastTemperature = bmp.sensor.temperature

def pressureAltitude():
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    global lastPressure
    global lastPressureAlt
    global maxAltPressure
    lastPressure = bmp.sensor.pressure  # millibars
    currentPressureAlt = round(((1 - (lastPressure / 1013.25)** 0.190284)) * 145366.45, 0)
    if currentPressureAlt > maxAltPressure:
        maxAltPressure = currentPressureAlt    

    #MAJOR BUG HERE!  NEED TO GET CORRECT number of seconds since last update
    LogFreqSeconds = 5

    verticalSpeedFps = round((currentPressureAlt - lastPressureAlt) / LogFreqSeconds, 1) # feet per second
    lastPressureAlt = currentPressureAlt
    return currentPressureAlt

def secondsSinceLastGoodFix():
    return  round((datetime.now() - lastGoodGpsFix).total_seconds(), 1)  #LastFix (seconds since)

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