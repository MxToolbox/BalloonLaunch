#!/usr/bin/env python3
#https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf

import time
import sys
import serial
import argparse 
import threading as thread
from serial.threaded import LineReader, ReaderThread
import zlib

TRANSMIT_FREQ = 5  # seconds
values = [0]*17  # These values get transmitted via compressed CSV


parser = argparse.ArgumentParser(description='LoRa Radio mode sender.')
parser.add_argument('port', help="Serial port descriptor")
args = parser.parse_args()

class PrintLines(LineReader):


    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd("sys set pindig GPIO11 0")
        self.send_cmd('radio set freq 903500000')        
        self.send_cmd('sys get ver')
        self.send_cmd('radio get mod')
        self.send_cmd('radio get freq')
        self.send_cmd('radio get sf')
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 20')
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = 0

    def handle_line(self, data):
        if data == "ok":
            return
        print("RECV: %s" % data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        # todo:  make this more fault tollerant by attempting reconnect.
        print("port closed")

    def tx(self):
        self.send_cmd("sys set pindig GPIO11 1")
        # delete some data to reduce packet size.
        values[2] = ''
        values[4] = ''
        #values[5] = ''        
        values[6] = ''
        values[7] = ''
        values[8] = ''
        values[9] = ''
        values[16] = ''

        valuesStr = ",".join(map(str,values))
        valueBin = zlib.compress(str.encode(valuesStr))
        telemetry = valueBin.hex()

        txmsg = 'radio tx ' + telemetry
        self.send_cmd(txmsg)
        time.sleep(.3)
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = self.frame_count + 1

    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s bytes " % str(len(cmd)) + cmd )
        self.write_line(cmd)
        time.sleep(delay)

def sendTelemetry():
    with ReaderThread(ser, PrintLines) as protocol:
        while(1):
            protocol.tx()
            time.sleep(TRANSMIT_FREQ)

print("Iniitializing LoRa Telemtry...")
ser = serial.Serial(args.port, baudrate=57600)
telemetry_thread=thread.Thread(target=sendTelemetry) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()