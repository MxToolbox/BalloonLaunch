import os
import time
import math
import logging
from datetime import datetime, timedelta 
import bmp280
import csvLog
import telemetry
import loraTx

LOCATION = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Starting data logger')

def pressureAltitude(millibars):
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    return round(((1 - (millibars / 1013.25)** 0.190284)) * 145366.45, 0)

tracker = telemetry
transmitter = loraTx
bmp = bmp280

maxAltPressure = 0 # feet
maxAltGps = 0  # meters

values = [0]*23
headers = [0]*23
headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time","maxAltGps","maxAltPressure", "HDOP", "VDOP", "LastFix", "Mode"]
csvLog.writeCsvLog(headers)

LogFreqSeconds = 1

lastPressureAlt = pressureAltitude(bmp.sensor.pressure)
lastGoodGpsFix = datetime.now()
lastGoodLat = math.nan
lastGoodLon = math.nan
lastGoodAlt = math.nan
hasGpsFix = False
while True:
    try:
        currentTime = datetime.now()
        values[0] = str(currentTime)
        values[1] = round(bmp.sensor.temperature, 3)    # celsius
        values[2] = round(0, 3) # Humidity
        values[3] = round(bmp.sensor.pressure, 3) # millibars

        pressureAlt = pressureAltitude(bmp.sensor.pressure)
        values[4] = round(pressureAlt, 0) # feet

        values[5] = round((pressureAlt - lastPressureAlt) / LogFreqSeconds, 1) # feet per second
        #values[6] = pitch, values[7] = roll, values[8] = yaw

        currentLat = tracker.gpsd.fix.latitude
        currentLon = tracker.gpsd.fix.longitude
        currentAlt = tracker.gpsd.fix.altitude
        if math.isnan(currentLat) or math.isnan(currentLon) or math.isnan(currentAlt):
            hasGpsFix = False
        else:
            hasGpsFix = True
            lastGoodLat = currentLat
            lastGoodLon = currentLon
            lastGoodAlt = currentAlt
            lastGoodGpsFix = datetime.now()

        values[10] =  lastGoodLat # LAT (from another sensor)
        values[11] =  lastGoodLon # LON (from another sensor)
        values[12] =  lastGoodAlt 
        values[13] = tracker.gpsd.fix.speed  
        values[14] = tracker.gpsd.fix.climb  
        values[15] = tracker.gpsd.fix.track 
        values[16] = tracker.gpsd.utc
        values[17] = maxAltGps
        values[18] = maxAltPressure
        values[19] = tracker.gpsd.hdop
        values[20] = tracker.gpsd.vdop
        values[21] = round((datetime.now() - lastGoodGpsFix).total_seconds(), 1)  #LastFix (seconds since)
        values[22] = 0  #Mode

        csvLog.writeCsvLog(values)
        i = 0
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(formatStr.format(headers[i],  v))
            i = i + 1
        print('________________________________________________')

        lastPressureAlt = pressureAlt  # for calculating vertical 
        transmitter.values = values
        
        # Check Max Alt
        if values[12] > maxAltGps:
            maxAltGps = values[12] 
        if values[4] > maxAltPressure:
            maxAltPressure = values[4] 

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        time.sleep(1)
    time.sleep(LogFreqSeconds)
