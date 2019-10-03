import os
import time
import csvLog
import gpsTrack
import loraTx
from datetime import datetime, timedelta 
from sense_hat import SenseHat

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

sense = SenseHat()
values = [0]*17
headers = [0]*17
headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time"]
formatStr = '| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>12} | {5:>10} | {6:>6} | {7:>6} | {8:>6} | {9:>6} | {10:>14} | {11:>14} | {12:>10} | {13:>10} | {14:>10} | {15:>10}'
print(formatStr.format(*headers))
csvLog.writeCsvLog(headers)
LogFreqSeconds = 1
lastPressureAlt = pressureAltitude(sense.pressure)
while True:
    try:
        sense.clear(255,255,255)  # Strobe effect while reading sensors
        currentTime = datetime.now()
        values[0] = str(currentTime)
        values[1] = round(sense.temp, 3)    # celsius
        values[2] = round(sense.humidity, 3) # %
        values[3] = round(sense.pressure, 3) # millibars

        pressureAlt = pressureAltitude(sense.pressure)
        values[4] = round(pressureAlt, 0) # feet

        values[5] = round((pressureAlt - lastPressureAlt) / LogFreqSeconds, 1) # feet per second
        orientation = sense.get_orientation_degrees()

        #sense.set_imu_config(False, True, True)  # gyroscope / accelerometer only
        values[6] = round(orientation["pitch"], 0)
        values[7] = round(orientation["roll"], 0)
        values[8] = round(orientation["yaw"], 0)

    # takessense.set_imu_config(True, False, False)  # compass only
        #values[9] = round(sense.get_compass(), 2)
        values[10] = tracker.gpsd.fix.latitude  # LAT (from another sensor)
        values[11] = tracker.gpsd.fix.longitude  # LON (from another sensor)
        values[12] = tracker.gpsd.fix.altitude  
        values[13] = tracker.gpsd.fix.speed  
        values[14] = tracker.gpsd.fix.climb  
        values[15] = tracker.gpsd.fix.track 
        values[16] = tracker.gpsd.utc 
        

        csvLog.writeCsvLog(values)
        #print(formatStr.format(*values))
        i = 0
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(formatStr.format(headers[i],  v))
            i = i + 1
        print('________________________________________________')

        lastPressureAlt = pressureAlt
        telemetry.values = values
        sense.clear()  # Strobe off
    except:
        print("Unhandled exception!")
        sense.clear(255,0,0)  # Strobe effect while reading sensors

    if tracker.gpsd.utc != '':
        setTimeFromGps(tracker.gpsd.utc)
    time.sleep(LogFreqSeconds)
    #sense.show_message("Hello world!")