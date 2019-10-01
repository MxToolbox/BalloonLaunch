#!/usr/bin/env python3
import time
import sys
import serial
import argparse 
import codecs
from serial.threaded import LineReader, ReaderThread
import curses
from colorama import Fore, Back, Style 
import csvLog

headers = ["time","temp","humidity","pressure","pressure alt","vert speed","pitch","roll","yaw","compass","lat","lon","gps alt","gps speed", "gps climb", "gps track", "gps time"]
csvLog.writeCsvLog(headers)
parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('port', help="Serial port descriptor")
args = parser.parse_args()

class PrintLines(LineReader):

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd('sys get ver')
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 10')
        self.send_cmd('radio rx 0')
        self.send_cmd("sys set pindig GPIO10 0")

    def handle_line(self, data):
        if data == "ok" or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return
        
        self.send_cmd("sys set pindig GPIO10 1", delay=0)
        print(data)
        try:
            parts = data.split(' ')
            command = parts[0]
            dataBytes = parts[2]
            if (command == 'radio_rx'):
                dataStr = codecs.decode(dataBytes, "hex").decode("utf-8")
                values =   dataStr.split(',')
                #print(command + ' ' + values)
                csvLog.writeCsvLog(values)
                i = 0          
                for v in values:
                    formatStr = '| {0:>15} | {1:>26} |'
                    print(formatStr.format(headers[i],  v))
                    i = i + 1
                print('________________________________________________')
            else:
                print(data)
        except:
            print("Ignoring decode error. ")

        time.sleep(.1)
        self.send_cmd("sys set pindig GPIO10 0", delay=1)
        self.send_cmd('radio rx 0')

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def send_cmd(self, cmd, delay=.5):
        self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        time.sleep(delay)

ser = serial.Serial(args.port, baudrate=57600)
#stdscr = curses.initscr()
#curses.noecho()
#curses.cbreak()
#begin_x = 20; begin_y = 7
#height = 5; width = 40
#win = curses.newwin(height, width, begin_y, begin_x)

with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        pass