#!/usr/bin/env python3
#https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf

# Thread about Rx window and watchdog timeouts....
#https://www.microchip.com/forums/m977377.aspx

import time
import sys
import serial
import argparse 
import threading as thread
from serial.threaded import LineReader, ReaderThread
import zlib
import codecs
import logging
import traceback

DataToTransmit = ""

ReceivedDataReady = False
ReceivedData = ""
RequestSNR = False
SNR = ""
DefaultReceive = False
def receiveCommand(RxData):
    global ReceivedDataReady
    global ReceivedData
    ReceivedData = RxData
    ReceivedDataReady = True

parser = argparse.ArgumentParser(description='LoRa Radio mode sender.')
parser.add_argument('--radio', help="Serial port descriptor")
args = parser.parse_args()

class Radio(LineReader):
    
    def connection_made(self, transport):
        global DefaultReceive
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
        if DefaultReceive:
            self.send_cmd('radio rx 0')  # set continuous receive
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = 0

    def RxStart(self):
        self.send_cmd('radio rx 0',2)  # set continous receive

    def RxStop(self):
        self.send_cmd('radio rxstop',2)  # end continous receive        

    def handle_line(self, data):
        global DefaultReceive
        global SNR
        #print(data)
        if data == "ok" or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return            
        
        # Decode RxData
        try:
            parts = data.split(' ')
            if len(parts) > 2 :
                print("Rx Data: " + data)
                command = parts[0]
                if command == "radio_rx":
                    self.send_cmd("sys set pindig GPIO10 1", delay=0) 
                    dataBytes = parts[2]     
                    RxData = zlib.decompress(codecs.decode(dataBytes, "hex")).decode("utf-8")
                    print("Rx " + str(len(data)) + " bytes: " + RxData)
                    receiveCommand(RxData)
                    if RequestSNR:
                        self.send_cmd('radio get snr')  # requires firmware 1.0.5 for RSSI
            else:
                print('INFO: ' + data)
                SNR = data
        except:
            print('ERROR: ' + data)
            logging.error("Exception occurred", exc_info=True)
            return           
        self.send_cmd("sys set pindig GPIO10 0", delay=1)

        if DefaultReceive:
            self.send_cmd('radio rx 0')  # set continuous receive


    def connection_lost(self, exc):
        if exc:
            print(exc)
        # todo:  make this more fault tolerant by attempting reconnect.
        print("port closed")

    def tx(self):
        global DataToTransmit
        global DefaultReceive
        dataBin = zlib.compress(str.encode(DataToTransmit)).hex()
        DataToTransmit = ""  # clear the message        
        if DefaultReceive:
            self.send_cmd("radio rxstop", 1) #disable conitunous receive mode
            self.send_cmd('radio tx ' + dataBin, 3)
            self.send_cmd("radio rx 0", 1) # re-enable conitunous receive mode 
        else:
            self.send_cmd("sys set pindig GPIO11 1")
            self.send_cmd('radio tx ' + dataBin, .3)    
            self.send_cmd("sys set pindig GPIO11 0")

    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s bytes " % str(len(cmd)) + cmd )
        self.write_line(cmd)
        time.sleep(delay)

def Transmit():
    with ReaderThread(ser, Radio) as protocol:
        while(1):
            if not DataToTransmit == "":
                protocol.tx()
            time.sleep(.1)

print("Iniitializing LoRa Radio...")
ser = serial.Serial(args.radio, baudrate=57600)
telemetry_thread=thread.Thread(target=Transmit) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()