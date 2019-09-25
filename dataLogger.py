import time
import csvLog
from datetime import datetime, timedelta 
from sense_hat import SenseHat

def pressureAltitude(millibars):
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # takes millibars, returns pressure altitude in feet.
    return round(((1 - (millibars / 1013.25)** 0.190284)) * 145366.45, 0)

sense = SenseHat()
values = [0]*10
headers = [0]*10
headers = ["time","temp","humidity","pressure","pressure alt","pitch","roll","yaw","lat","lon"]
print('| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>12} | {5:>6} | {6:>6} | {7:>6} | {8:>6} | {8:>6} |'.format(*headers))
csvLog.writeCsvLog(headers)
while True:
    values[0] = str(datetime.now())
    values[1] = round(sense.temp, 3)    # celsius
    values[2] = round(sense.humidity, 3) # %
    values[3] = round(sense.pressure, 3) # millibars
    values[4] = round(pressureAltitude(sense.pressure), 0) # feet
    orientation = sense.get_orientation_degrees()
    values[5] = round(orientation["pitch"], 0)
    values[6] = round(orientation["roll"], 0)
    values[7] = round(orientation["yaw"], 0)
    values[8] = "0.0"  # LAT (from another sensor)
    values[9] = "0.0"  # LON (from another sensor)
    csvLog.writeCsvLog(values)

    print('| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>12} | {5:>6} | {6:>6} | {7:>6} | {8:>6} | {8:>6} |'.format(*values))
    time.sleep(5)
    #sense.show_message("Hello world!")