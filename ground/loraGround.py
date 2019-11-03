#!/usr/bin/env python3
#https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf

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
        print("connection made")
        self.transport = transport
        self.send_cmd('radio set freq 903500000')
        self.send_cmd('radio set mod lora') 
        self.send_cmd('sys get ver')
        self.send_cmd('radio get mod')
        self.send_cmd('radio get freq')
        self.send_cmd('radio get sf')        
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 20')        
        self.send_cmd('radio rx 0')
        self.send_cmd("sys set pindig GPIO10 0")        

    def handle_line(self, data):
        print(data)
        global snr
        if data == "ok": #or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return
        
        sendingCommand = ""

        # Decode RxData
        try:
            parts = data.split(' ')
            if len(parts) > 2 :
                print("Rx Data: " + data)
                command = parts[0]
                if command == "radio_rx":
                    self.send_cmd("sys set pindig GPIO10 1", delay=0) 
                    dataBytes = parts[2]     
                    print("Rx " + str(len(data)) + " bytes: " + str(dataBytes)) 
                    RxData = zlib.decompress(codecs.decode(dataBytes, "hex")).decode("utf-8")
                    print("RECV COMMAND: %s" % RxData)
                    receiveCommand(RxData)
                    self.send_cmd('radio rx 0')
                    if RequestSNR:
                        self.send_cmd('radio get snr')  # requires firmware 1.0.5 for RSSI
                    self.send_cmd("sys set pindig GPIO10 0", delay=1)
            else:
                print('INFO: ' + data)
                SNR = data
        except:
            print('ERROR: ' + data)
            logging.error("Exception occurred", exc_info=True)
            return   
        #self.send_cmd('radio rx 0')

        if not sendingCommand == "":
            print("Sending?")
            self.tx()
            sendingCommand = ""  #clear command

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def tx(self):
        global DataToTransmit
        self.send_cmd("sys set pindig GPIO11 1")
        dataBin = zlib.compress(str.encode(DataToTransmit)).hex()
        DataToTransmit = ""  # clear the message
        txmsg = 'radio tx ' + dataBin
        self.send_cmd(txmsg)
        time.sleep(.3)
        self.send_cmd("sys set pindig GPIO11 0")

    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s bytes " % str(len(cmd)) + cmd )
        self.write_line(cmd)
        time.sleep(delay)

snr = -99
parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('--radio', help="Serial port descriptor")
#parser.add_argument('--gps', help="Serial port descriptor")
args = parser.parse_args()
ser = serial.Serial(args.radio, baudrate=57600)
def Transmit():
    with ReaderThread(ser, Radio) as protocol:
        while(1):
            if not DataToTransmit == "":
                protocol.tx()
            time.sleep(.1)   

print("Iniitializing LoRa Radio...")
telemetry_thread=thread.Thread(target=Transmit) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()
