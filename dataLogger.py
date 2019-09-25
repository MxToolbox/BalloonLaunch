import time
import csvLog
from datetime import datetime, timedelta 
from sense_hat import SenseHat

def pressureAltitude(millibars):
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    return round(((1 - (millibars / 1013.25)** 0.190284)) * 145366.45, 0)

sense = SenseHat()
values = [0]*12
headers = [0]*12
headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon"]
formatStr = '| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>12} | {5:>10} | {6:>6} | {7:>6} | {8:>6} | {9:>6} | {10:>6} | {11:>6} '
print(formatStr.format(*headers))
csvLog.writeCsvLog(headers)
LogFreqSeconds = 5
lastPressureAlt = pressureAltitude(sense.pressure)
while True:
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
    values[10] = "0.0"  # LAT (from another sensor)
    values[11] = "0.0"  # LON (from another sensor)
    csvLog.writeCsvLog(values)
    print(formatStr.format(*values))

    lastPressureAlt = pressureAlt
    sense.clear()  # Strobe off
    time.sleep(LogFreqSeconds)
    #sense.show_message("Hello world!")