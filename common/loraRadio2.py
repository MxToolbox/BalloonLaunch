#!/usr/bin/env python3
# https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf
# Note requires RN2482 firmware 1.0.5 for the new rxstop command  (https://www.microchip.com/forums/m977377.aspx)

import time
from datetime import datetime, timedelta 
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
    # used for verifying commands have completed.
    lastCommand = ""
    #lastSendTime = datetime.now()
    waitingForResponse = False
    lastResponse = ""

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd('radio set freq 903500000', False)        
        self.send_cmd('radio set pwr 20')
        #self.send_cmd('sys get ver')
        #self.send_cmd('radio get mod')
        #self.send_cmd('radio get freq')
        #self.send_cmd('radio get sf')
        self.send_cmd('mac pause')
        self.send_cmd('radio rx 0')  # Continuous Receive mode
        self.frame_count = 0

    def handle_line(self, data):
        print(data)
        if self.waitingForResponse:
            self.lastResponse = data
            print("Response: " + self.lastResponse)
            self.waitingForResponse = False
            if data == "radio_err":
                print(data)
                self.send_cmd('radio rx 0')
            return
        if data == "ok":
            return
       
        
        # Decode RxData
        try:
            parts = data.split(' ')
            if len(parts) > 2 :
                print("Rx Data: " + data)
                command = parts[0]
                if command == "radio_rx":
                    #self.send_cmd("sys set pindig GPIO10 1") 
                    dataBytes = parts[2]     
                    print("Rx " + str(len(data)) + " bytes: " + str(dataBytes)) 
                    RxData = zlib.decompress(codecs.decode(dataBytes, "hex")).decode("utf-8")
                    print("RECV COMMAND: %s" % RxData)
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
        #self.send_cmd("sys set pindig GPIO10 0")
        self.send_cmd('radio rx 0')  


    def connection_lost(self, exc):
        if exc:
            print(exc)
        # todo:  make this more fault tolerant by attempting reconnect.
        print("port closed")

    def tx(self):
        global DataToTransmit
        self.send_cmd("radio rxstop")  # end continuous receive mode so we can transmit
        #self.send_cmd("sys set pindig GPIO11 1")
        dataBin = zlib.compress(str.encode(DataToTransmit)).hex()
        DataToTransmit = ""  # clear the message
        txmsg = 'radio tx ' + dataBin
        self.send_cmd(txmsg)
        #self.send_cmd("sys set pindig GPIO11 0")
        self.send_cmd('radio rx 0')  # reenable continuous receive mode


    #def send_cmd_old(self, cmd, delay=.5):
    #    print("SEND: %s bytes " % str(len(cmd)) + cmd )
    #    self.write_line(cmd)
    #    time.sleep(delay)

    # send and wait for and return response
    def send_cmd(self, cmd, expectResponse = True):
        #delay is ignored here!
        print("SEND: %s bytes " % str(len(cmd)) + cmd )
        self.write_line(cmd)
        time.sleep(1)
        if expectResponse:
            self.waitingForResponse = True
            self.lastCommand = cmd
            while self.waitingForResponse == True:
                time.sleep(.05)
                print("Waiting on " + self.lastCommand)
                return self.lastResponse
        else:
            return ""

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