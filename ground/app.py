#!/usr/bin/env python3
import sys
import os
import time
import traceback
import math
import numpy
from colorama import Fore, Back, Style, init
import zlib
from geographiclib.geodesic import Geodesic
import logging
import winsound  #windows only
import gpsFileWatcher
import csvLog
import loraRx
sys.path.insert(1, '../common/')
import flightModes
import voiceStatus

receiver = loraRx
gpsWatcher = gpsFileWatcher
fmode = flightModes.Modes()
voice = voiceStatus
init()  # colorama

logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Initializing Ground Control')


rxPositionSet = False
rxLat = 30.4316015
rxLon = -97.7660455
rxAlt = 800  #feet
txLat = 0.0
txLon = 0.0
rssi = ""

headers = ["time","temp","humidity","pressure","pressure alt (ft)","vert speed (ft/s)","pitch","roll","yaw","compass","lat","lon","gps alt (m)","gps speed (m/s)", "gps climb (m/s)", "gps track", "gps time","maxAltGps (m)","maxAltPressure (ft)", "HDOP", "VDOP", "LastFix", "Mode", "down range (m)", "heading", "snr", "rx lat", "rx lon", "rx alt", "elevation", "los range (m)"]
colors = [Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE]
csvLog.writeCsvLog(headers)

# Poll for new data
while True:
    if receiver.dataReady:
        # Calc geo range / heading
        try:
            values = receiver.values
            txAlt = round(((1 - (float(values[3]) / 1013.25)** 0.190284)) * 145366.45, 0)  # calc pressure alt from pressure
            values[4] = txAlt  #pressure alt (feet)
            txLat = float(values[10])
            txLon = float(values[11])
            lastFix = float(values[21])
            if (rxPositionSet == False):
                rxPositionSet = True
                rxLat = txLat
                rxLon = txLon
                rxAlt = txAlt
                print("Receiver position synced with transmitter position: " + str(rxLat) + ' , ' + str(rxLon) )

            # Decode and output mode status
            fmode.SetModeBitArray(values[22])
            print(fmode.StatusMessage())
            voiceStatus.engine.say(fmode.StatusMessage())

            rxLat = round(gpsWatcher.latitude,6)  # Geo from local GPS on transer device
            rxLon = round(gpsWatcher.longitude,6)
            rxAlt = int(gpsWatcher.altitude)

            geo = Geodesic.WGS84.Inverse(rxLat, rxLon, txLat, txLon)
            distance = 0
            azimuth = 0
            if math.isnan(rxLat) or math.isnan(rxLon) or math.isnan(txLat)  or math.isnan(txLon) or lastFix > 60.0:
                msg = "Missing GPS Fix.  Last fix was " + str(round(lastFix/60,1)) + " minutes ago!"
                print(Fore.RED,msg )
                frequency = 500  # lower tone
                duration = 350  # longer duration 
            else:                
                distance = int(geo['s12'])
                azimuth = int(geo['azi1'])
                frequency = 2500  # higher tone
                duration = 250  # shorter duration 
            
            if azimuth < 0:
                azimuth = 360 + azimuth
            values.append(distance)
            values.append(azimuth)
            values.append(receiver.snr)
            values.append(rxLat)
            values.append(rxLon)
            values.append(rxAlt)
            

            elevation = 0
            los_range = 0
            if distance > 0:
                altDeltaMeters = (txAlt / 3.28) - rxAlt  #txAlt is pressure alt in feet!
                elevation = str(int((numpy.arctan(altDeltaMeters / distance)) * 57.2958))  #radians to degrees
                los_range = math.sqrt(altDeltaMeters**2 + distance**2)
            values.append(round(float(elevation),1))  #elevation
            values.append(int(los_range))  #los range accounting for elevation

            csvLog.writeCsvLog(values)
            winsound.Beep(frequency, duration)

            # display output
            print(' _____________________________________________________')
            i = 0          
            for v in values:
                formatStr = '| {0:>20} | {1:<26} |'
                print(colors[i] ,formatStr.format(headers[i],  v))
                i = i + 1
            print(' _____________________________________________________')
        except:
            print("Exception")
            logging.error("Exception occurred", exc_info=True)
        finally:
            receiver.dataReady = False        
    else:
        time.sleep(1)
