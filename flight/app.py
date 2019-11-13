import sys
import os
import time
import math
import logging
from datetime import datetime, timedelta 
import RPi.GPIO as GPIO
import csvLog
import telemetry
sys.path.insert(1, 'common/')
import loraRadio
import flightModes
import atexit
#import raspistills  
import flightGPIO
import codecs
import messages
import ina219meter
import si1145

def cleanup():
    flightGPIO.destroy()

atexit.register(cleanup)

GPIO.cleanup()          # just in case?
GPIO.setmode(GPIO.BCM)  # global for the app


LOCATION = os.path.dirname(os.path.abspath(__file__))
#logging.basicConfig(level=logging.DEBUG,filename='mdm-2.log', format='%(process)d-%(levelname)s-%(message)s')
logging.basicConfig(level=logging.DEBUG,filename='mdm-2.log')
logger = logging.getLogger()
logger.warning('Starting Flight Computer')

tracker = telemetry
radio = loraRadio
uv = si1145.SI1145()

values = [0]*28
headers = [0]*28
headers = ["time","temp","humidity", "pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time","maxAltGps","maxAltPressure", "HDOP", "VDOP", "LastFix", "Mode", "Message", "voltage", "current", "uvindex", "uv"]
csvLog.writeCsvLog(headers)

LogFreqSeconds = 10
radio.DefaultReceive = True
lastMessageCode = 250
while True:
    try:        
        # Check for any new commands from Ground
        if loraRadio.ReceivedDataReady:
            command = loraRadio.ReceivedData
            print("Received Command: " + command)
            loraRadio.ReceivedData = ""       #reset semaphore and value
            loraRadio.ReceivedDataReady = False
            if command == "cutdown":
                flightGPIO.CutdownArmed = True
                lastMessageCode = flightGPIO.CutDownEnergize(tracker.fmode.GroundProximity)
                flightGPIO.CutdownArmed = False
            if command == "gps-airborne":
                tracker.ublox8.setUbloxDynamicMode(6, True)
                lastMessageCode = 270
            if command == "gps-portable":
                tracker.ublox8.setUbloxDynamicMode(0, True)
                lastMessageCode = 270                

        tracker.update()
        values[0] = str(datetime.now())
        values[1] = round(tracker.lastTemperature, 2)    # celsius
        values[2] = round(0, 0) # Humidity
        values[3] = round(tracker.lastPressure, 3) # millibars
        values[4] = round(tracker.lastPressureAlt, 0) # feet
        values[5] = round(tracker.verticalSpeed, 0)
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
        values[23] = lastMessageCode

        values[24] = ina219meter.voltage()
        values[25] = ina219meter.current()
        values[26] = uv.readUV()
        values[27] = "0"

        flightGPIO.IsGroundAlarm = tracker.fmode.GroundProximity
        
        csvLog.writeCsvLog(values)

        # print local debug
        i = 0
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(formatStr.format(headers[i],  v))
            i = i + 1
        print('________________________________________________')

        # delete some data to reduce packet size.
        values[2] = ''
        values[4] = ''
        values[6] = ''
        values[7] = ''
        values[8] = ''
        values[9] = ''
        
        values[16] = ''
        valuesStr = ",".join(map(str,values))

        # queue for transmission
        loraRadio.DataToTransmit = valuesStr
        lastMessageCode = 250
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        lastMessageCode = 500
        time.sleep(1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print("Ctrl+C Exiting....")
        flightGPIO.destroy()
    time.sleep(LogFreqSeconds)
