import time
import csvLog
from datetime import datetime, timedelta 
from sense_hat import SenseHat

sense = SenseHat()
values = [0]*9
headers = [0]*9
headers = ["time","temp","humidity","pressure","pitch","roll","yaw","lat","lon"]
print('| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>6} | {5:>6} | {6:>6} | {7:>6} | {8:>6} |'.format(*headers))
csvLog.writeCsvLog(headers)
while True:
    values[0] = str(datetime.now())
    values[1] = round(sense.temp, 3)    # celsius
    values[2] = round(sense.humidity, 3) # %
    values[3] = round(sense.pressure, 3) # millibars
    orientation = sense.get_orientation_degrees()
    values[4] = round(orientation["pitch"], 0)
    values[5] = round(orientation["roll"], 0)
    values[6] = round(orientation["yaw"], 0)
    values[7] = "0.0"  # LAT (from another sensor)
    values[8] = "0.0"  # LON (from another sensor)
    csvLog.writeCsvLog(values)

    print('| {0:>26} | {1:>6} | {2:>8} | {3:>8} | {4:>6} | {5:>6} | {6:>6} | {7:>6} | {8:>6} |'.format(*values))
    time.sleep(5)
    #sense.show_message("Hello world!")