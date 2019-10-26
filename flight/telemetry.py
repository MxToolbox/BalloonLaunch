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
#mode = flightModes
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

lastUpdate = datetime.now()
def update():
    global lastUpdate 
    global lastGoodLat
    global lastGoodLon 
    global lastGoodAlt 
    global lastGoodGpsFix 
    global lastTemperature
    global maxAltGps
    lastUpdate = datetime.now()

    currentLat = gpsd.fix.latitude
    currentLon = gpsd.fix.longitude
    currentAlt = gpsd.fix.altitude
    if math.isnan(currentLat) or math.isnan(currentLon) or math.isnan(currentAlt):
        flightModes.hasGpsFix = False
        # This prevents overriding the last known Fix with NaN
    else:
        flightModes.hasGpsFix = True
        lastGoodLat = round(currentLat, 4)
        lastGoodLon = round(currentLon, 4)
        lastGoodAlt = int(currentAlt)
        lastGoodGpsFix = datetime.now()    
        # Check Max GPS Alt
        if lastGoodAlt > maxAltGps:
            maxAltGps = lastGoodAlt 
    
    # Update PressureAlt / Temp
    pressureAltitude()  

def pressureAltitude():
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    global lastPressure
    global lastPressureAlt
    global maxAltPressure
    global verticalSpeedFps
    lastPressure = int(bmp.sensor.pressure)  # millibars
    currentPressureAlt = round(((1 - (lastPressure / 1013.25)** 0.190284)) * 145366.45, 0)
    if currentPressureAlt > maxAltPressure:
        maxAltPressure = int(currentPressureAlt)

    verticalSpeedFps = round((currentPressureAlt - lastPressureAlt) / secondsSinceLastUpdate(), 1) # feet per second
    lastPressureAlt = int(currentPressureAlt)
    lastTemperature = bmp.sensor.temperature
    return currentPressureAlt

def secondsSinceLastGoodFix():
    return  round((datetime.now() - lastGoodGpsFix).total_seconds(), 1)  #LastFix (seconds since)

def secondsSinceLastUpdate():
    seconds = round((datetime.now() - lastUpdate).total_seconds(), 1) 
    if seconds == 0:
        seconds = 1  #prevent div/0
    return  seconds

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