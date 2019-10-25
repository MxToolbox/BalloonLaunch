import os
import time
import math
import logging
import csvLog
import gpsTrack
import loraTx
from datetime import datetime, timedelta 
import bmp280
bmp = bmp280

LOCATION = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Starting data logger')


def pressureAltitude(millibars):
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    return round(((1 - (millibars / 1013.25)** 0.190284)) * 145366.45, 0)

hasSetTime = False
def setTimeFromGps(date_str):
    global hasSetTime
    if hasSetTime == False:
        os.system('hwclock --set --date %s' % date_str)
        print("hwclock set via GPS time: " + date_str)
        hasSetTime = True

tracker = gpsTrack
telemetry = loraTx


maxAltPressure = 0 # feet
maxAltGps = 0  # meters

values = [0]*23
headers = [0]*23
headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time","maxAltGps","maxAltPressure", "HDOP", "VDOP", "LastFix", "Mode"]
formatStr = '| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>12} | {5:>10} | {6:>6} | {7:>6} | {8:>6} | {9:>6} | {10:>14} | {11:>14} | {12:>10} | {13:>10} | {14:>10} | {15:>10}'
print(formatStr.format(*headers))
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
        #sense.set_pixel(0, 0, (0, 0, 255))

        currentTime = datetime.now()
        values[0] = str(currentTime)
        values[1] = round(bmp.sensor.temperature, 3)    # celsius
        values[2] = round(0, 3) # Humidity
        values[3] = round(bmp.sensor.pressure, 3) # millibars

        pressureAlt = pressureAltitude(bmp.sensor.pressure)
        values[4] = round(pressureAlt, 0) # feet

        values[5] = round((pressureAlt - lastPressureAlt) / LogFreqSeconds, 1) # feet per second
        #orientation = metrics.orientation_degrees


        #values[6] = round(orientation["pitch"], 0)
        #values[7] = round(orientation["roll"], 0)
        #values[8] = round(orientation["yaw"], 0)
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
        #print(formatStr.format(*values))
        i = 0
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(formatStr.format(headers[i],  v))
            i = i + 1
        print('________________________________________________')

        lastPressureAlt = pressureAlt  # for calculating vertical 
        telemetry.values = values
        
        # Check Max Alt
        if values[12] > maxAltGps:
            maxAltGps = values[12] 
        if values[4] > maxAltPressure:
            maxAltPressure = values[4] 

        #sense.clear()  # Strobe off
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        #sense.clear(255,0,0)  # Flash RED on error
        time.sleep(1)
        #sense.clear()  # Strobe off
    #if tracker.gpsd.utc != '':
    #    setTimeFromGps(tracker.gpsd.utc)
    time.sleep(LogFreqSeconds)
    #sense.show_message("Hello world!")