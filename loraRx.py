#!/usr/bin/env python3
import os
import time
import sys
import serial
import argparse 
import codecs
from serial.threaded import LineReader, ReaderThread
#import curses
from colorama import Fore, Back, Style, init
import csvLog
import zlib
from geographiclib.geodesic import Geodesic
#init()
# rxLat = 30.4196
# rxLon = -97.8

rxLat = 30.4316015
rxLon = -97.7660455
txLat = 0.0
txLon = 0.0
rssi = ""

headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time", "range (m)", "heading", "rssi"]
csvLog.writeCsvLog(headers)
parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('port', help="Serial port descriptor")
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
        global txLat
        global txLon
        global rssi

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
            values =   dataStr.split(',')
        except:
            rssi = data
            print('INFO: ' + data)
            return

        # Calc geo range / heading
        try:
            txLat = float(values[10])
            txLon = float(values[11])
            geo = Geodesic.WGS84.Inverse(txLat, txLon, rxLat, rxLon)
            distance = int(geo['s12'])
            azimuth = int(geo['azi1'])
            if azimuth < 0:
                azimuth = 360 + azimuth
            values.append(distance)
            values.append(azimuth)
        except:
            print("Error calulating GEO data")
            return
        values.append(rssi)

        csvLog.writeCsvLog(values)

        # display output
        clear()
        print('________________________________________________')
        i = 0          
        for v in values:
            formatStr = '| {0:>15} | {1:>26} |'
            print(Fore.YELLOW,formatStr.format(headers[i],  v))
            #print(Style.RESET_ALL) 
            i = i + 1
        print('________________________________________________')
        print(str(len(data)) + " bytes")
        time.sleep(.1)
        self.send_cmd("sys set pindig GPIO10 0", delay=1)
        self.send_cmd('radio rx 0')
        self.send_cmd('radio get rssi')  # requires firmware 1.0.5
    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def send_cmd(self, cmd, delay=.5):
        self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(delay)

ser = serial.Serial(args.port, baudrate=57600)
with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        pass