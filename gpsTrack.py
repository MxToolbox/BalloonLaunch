import os
import time
from gps import *

import threading as thread
gpsd = None

def refreshGpsd():
    global gpsd
    while True:
        gpsd.next()
        time.sleep(.1)  
        # print("hello")
    

print("Iniitializing GPSD...")
gpsd = gps(mode=WATCH_ENABLE) 
tracker_thread=thread.Thread(target=refreshGpsd) 
tracker_thread.setDaemon(True)                  
tracker_thread.start()  