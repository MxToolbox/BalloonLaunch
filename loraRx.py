#!/usr/bin/env python3
import os
import time
import sys
import traceback
import math
import numpy
import serial
import argparse 
import codecs
from serial.threaded import LineReader, ReaderThread
from colorama import Fore, Back, Style, init
import csvLog
import zlib
from geographiclib.geodesic import Geodesic
import logging
import winsound  #windows only
import gpsFileWatcher

init()

gpsWatcher = gpsFileWatcher

logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Starting data logger')

rxPositionSet = False
rxLat = 30.4316015
rxLon = -97.7660455
rxAlt = 800  #feet
txLat = 0.0
txLon = 0.0
rssi = ""

headers = ["time","temp","humidity","pressure","pressure alt (ft)","vert speed (ft/s)","pitch","roll","yaw","compass","lat","lon","gps alt (m)","gps speed (m/s)", "gps climb (m/s)", "gps track", "gps time","maxAltGps (m)","maxAltPressure (ft)", "down range (m)", "heading", "snr", "rx lat", "rx lon", "rx alt", "elevation", "los range (m)"]
colors = [Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.WHITE,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.CYAN,Fore.WHITE,Fore.WHITE,Fore.WHITE]
csvLog.writeCsvLog(headers)
parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('--radio', help="Serial port descriptor")
parser.add_argument('--gps', help="Serial port descriptor")
args = parser.parse_args()
clear = lambda: os.system('cls')  #'clear' for linux
class PrintLines(LineReader):


    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd('radio set freq 903500000') 
        self.send_cmd('sys get ver')
        self.send_cmd('radio get mod')
        self.send_cmd('radio get freq')
        self.send_cmd('radio get sf')        
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 20')
        
      
        self.send_cmd('radio rx 0')
        self.send_cmd("sys set pindig GPIO10 0")

    def handle_line(self, data):
        global rxLat
        global rxLon
        global rxAlt 
        global txLat
        global txLon
        global rssi
        global rxPositionSet
        if data == "ok" or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return
        self.send_cmd("sys set pindig GPIO10 1", delay=0)

        # try to  parse & decode data 
        try:     
            parts = data.split(' ')
            command = parts[0]
            dataBytes = parts[2]     
            dataStr = zlib.decompress(codecs.decode(dataBytes, "hex")).decode("utf-8")
            #print(dataStr)
            values =   dataStr.split(',')
        except:
            rssi = data
            print('INFO: ' + data)
            return

        # Calc geo range / heading
        try:
            txAlt = round(((1 - (float(values[3]) / 1013.25)** 0.190284)) * 145366.45, 0)  # calc pressure alt from pressure
            values[4] = txAlt  #pressure alt (feet)
            txLat = float(values[10])
            txLon = float(values[11])
            if (rxPositionSet == False):
                rxPositionSet = True
                rxLat = txLat
                rxLon = txLon
                rxAlt = txAlt
                print("Receiver position synced with transmitter position: " + str(rxLat) + ' , ' + str(rxLon) )

            rxLat = round(gpsWatcher.latitude,6)  # Geo from local GPS on transer device
            rxLon = round(gpsWatcher.longitude,6)
            rxAlt = int(gpsWatcher.altitude)

            geo = Geodesic.WGS84.Inverse(rxLat, rxLon, txLat, txLon)
            distance = 0
            azimuth = 0
            if math.isnan(rxLat) or math.isnan(rxLon) or math.isnan(txLat)  or math.isnan(txLon):
                print("Missing GPS Fix")
            else:                
                distance = int(geo['s12'])
                azimuth = int(geo['azi1'])
            
            if azimuth < 0:
                azimuth = 360 + azimuth
            values.append(distance)
            values.append(azimuth)
            values.append(rssi)
            values.append(rxLat)
            values.append(rxLon)
            values.append(rxAlt)
            

            elevation = 0
            los_range = 0
            if distance > 0:
                altDeltaMeters = (txAlt / 3.28) - rxAlt  #txAlt is pressure alt in feet!
                #print(altDeltaMeters)
                elevation = str(int((numpy.arctan(altDeltaMeters / distance)) * 57.2958))  #radians to degrees
                #elevation = str(math.tan(altDeltaMeters / distance))
                los_range = math.sqrt(altDeltaMeters**2 + distance**2)
            values.append(round(float(elevation),1))  #elevation
            values.append(int(los_range))  #los range accounting for elevation

        except:
            print("Error calulating GEO data " + traceback.format_exc())


        csvLog.writeCsvLog(values)

        frequency = 3500  # Set Frequency To 2500 Hertz
        duration = 250  # Set Duration To 1000 ms == 1 second      
        winsound.Beep(frequency, duration)

        # display output
        #clear()
        print(' _____________________________________________________')
        i = 0          
        for v in values:
            formatStr = '| {0:>20} | {1:<26} |'
            print(colors[i] ,formatStr.format(headers[i],  v))
            #print(Style.RESET_ALL) 
            i = i + 1
        print(' _____________________________________________________')
        print(str(len(data)) + " bytes")
        time.sleep(.1)
        try:
            self.send_cmd("sys set pindig GPIO10 0", delay=1)
            self.send_cmd('radio rx 0')
            self.send_cmd('radio get snr')  # requires firmware 1.0.5
        except:
            print("Possible Access denied error while writing! Press ENTER to continue...")
            #Warning:  comment out the line below!
            input1 = input() 

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def send_cmd(self, cmd, delay=.5):
        self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(delay)

# Main loop
ser = serial.Serial(args.radio, baudrate=57600)
with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        time.sleep(.1)
        pass
        
