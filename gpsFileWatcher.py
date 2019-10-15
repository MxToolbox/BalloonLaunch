# Watches a file for changes in GPS position (typically output from winlocation.ps1 every 5 seconds)

import os
import time
import logging

import threading as thread
LOCATION = os.path.dirname(os.path.abspath(__file__))
latitude = 0.0
longitude = 0.0
altitude = 0.0

def refreshGps():
    global latitude
    global longitude
    global altitude        
    while True:
        fp = open(LOCATION + '\\location.txt', 'r', encoding='utf-8')
        lines = fp.readlines()
        #print(lines[4])
        latitude = float(lines[2].split(': ')[1].replace(' ', ''))
        longitude = float(lines[3].split(': ')[1].replace(' ', ''))
        altitude = float(lines[4].split(': ')[1].replace(' ', ''))
        #print(latitude, longitude, altitude)
        fp.close()
        time.sleep(1)  

    
logging.info('Iniitializing GPS File Watcher...')
print("Iniitializing GPS File Watcher...")
tracker_thread=thread.Thread(target=refreshGps) 
tracker_thread.setDaemon(True)                  
tracker_thread.start()  