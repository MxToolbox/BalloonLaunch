import os
import time
import math
import logging
from datetime import datetime, timedelta 
import csvLog
import telemetry
import loraTx
import sys
sys.path.insert(1, 'common/')
import flightModes
import raspistills  
import proximityAlarm

LOCATION = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Starting data logger')

tracker = telemetry
transmitter = loraTx

values = [0]*23
headers = [0]*23
headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time","maxAltGps","maxAltPressure", "HDOP", "VDOP", "LastFix", "Mode"]
csvLog.writeCsvLog(headers)

LogFreqSeconds = 5
while True:
    try:
        tracker.update()

        #proximityAlarm.GpsAltitudeMeters = tracker.gpsd.fix.altitude
        #proximityAlarm.PressureAltitudeMeters = tracker.lastPressureAlt / 3.28
        values[0] = str(datetime.now())
        values[1] = round(tracker.lastTemperature, 2)    # celsius
        values[2] = round(0, 0) # Humidity
        values[3] = round(tracker.lastPressure, 3) # millibars
        values[4] = round(tracker.lastPressureAlt, 0) # feet
        values[5] = round(tracker.verticalSpeedFps, 0)
        #values[6] = pitch, values[7] = roll, values[8] = yaw

        values[10] =  tracker.lastGoodLat # LAT (from another sensor)
        values[11] =  tracker.lastGoodLon # LON (from another sensor)
        values[12] =  tracker.lastGoodAlt 
        values[13] = tracker.gpsd.fix.speed  
        values[14] = tracker.gpsd.fix.climb  
        values[15] = tracker.gpsd.fix.track 
        values[16] = tracker.gpsd.utc
        values[17] = tracker.maxAltGps
        values[18] = tracker.maxAltPressure
        values[19] = tracker.gpsd.hdop
        values[20] = tracker.gpsd.vdop
        values[21] = tracker.secondsSinceLastGoodFix()
        values[22] = tracker.fmode.GetModeBitArray() #Mode
        proximityAlarm.IsGroundAlarm = tracker.fmode.GroundProximity
        
        csvLog.writeCsvLog(values)

        # print local debug
        i = 0
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(formatStr.format(headers[i],  v))
            i = i + 1
        print('________________________________________________')

        transmitter.values = values

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        time.sleep(1)
    time.sleep(LogFreqSeconds)
