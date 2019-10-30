import os
import time
import math
import logging
from datetime import datetime, timedelta 
from gps import *
import threading as thread
import bmp280
sys.path.insert(1, '../common/')
import flightModes


GROUND_PROX_METERS = 600
gpsd = None 
fmode = flightModes.Modes()
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
IsArmed = False
THRESHOLD_ALTITUDE_METERS = 600  # arm once above this altitude, alarm after arming when falls below this altitude
def IsGroundAlarm(GpsAltitudeMeters,PressureAltitudeMeters):
	global IsArmed
	altMeters = 0 
	try:
		altMeters = int(GpsAltitudeMeters)
	except:
		try:
			altMeters = int(PressureAltitudeMeters)
		except:
			print("Unable to get altitude from GPS or altimeter!")

	if altMeters > THRESHOLD_ALTITUDE_METERS:
		IsArmed = True
	if IsArmed and altMeters < THRESHOLD_ALTITUDE_METERS:
		print("Gound Alarm")
		return True
	else:
		return False


def update():
    global lastUpdate 
    global lastGoodLat
    global lastGoodLon 
    global lastGoodAlt 
    global lastGoodGpsFix 
    global lastTemperature
    global maxAltGps
    global lastPressureAlt
    global verticalSpeedFps
    global fmode
    lastUpdate = datetime.now()
    currentLat = gpsd.fix.latitude
    currentLon = gpsd.fix.longitude
    currentAlt = gpsd.fix.altitude
    if math.isnan(currentLat) or math.isnan(currentLon) or math.isnan(currentAlt):
        fmode.HasGpsFix = False
        print("No Gps Fix, preserving last known fix.")
    else:
        fmode.HasGpsFix = True
        lastGoodLat = round(currentLat, 4)
        lastGoodLon = round(currentLon, 4)
        lastGoodAlt = int(currentAlt)
        lastGoodGpsFix = datetime.now()    
        # Check Max GPS Alt
        if lastGoodAlt > maxAltGps:
            maxAltGps = lastGoodAlt 
    
    fmode.GroundProximity = IsGroundAlarm(lastGoodAlt, lastPressureAlt / 3.28)
    #fmode.Stationary = fmode.GroundProximity &  verticalSpeedFps == 0

    if verticalSpeedFps > 0:
        fmode.Ascending = True
        fmode.Descending = False
        fmode.Stationary = False
    elif verticalSpeedFps < 0:
        fmode.Ascending = False
        fmode.Descending = True
        fmode.Stationary = False
    else:
        fmode.Ascending = False
        fmode.Descending = False
        fmode.Stationary = True           

    # Update PressureAlt / Temp
    pressureAltitude()  

def pressureAltitude():
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    try:
        global lastTemperature
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
    except:
        print("Error in pressureAltitude()")

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