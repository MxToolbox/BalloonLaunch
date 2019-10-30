import time
import serial
import argparse 
import threading as thread
import logging
import codecs
import traceback
import zlib
from serial.threaded import LineReader, ReaderThread


values = [0]
dataReady = False
CommandToSend = ""
snr = -99
def receiveValues(dataValues):
    global values
    global dataReady
    global CommandToSend
    values = dataValues
    dataReady = True  # semaphore that we have new data
    if not CommandToSend == "":
        sendingCommand = CommandToSend
        CommandToSend = ""
        return sendingCommand
    else:
        return ""

class RxGround(LineReader):

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
        #print(data)
        global snr
        if data == "ok" or data == 'busy':
            return
        if data == "radio_err":
            self.send_cmd('radio rx 0')
            return
        self.send_cmd("sys set pindig GPIO10 1", delay=0)
        sendingCommand = ""

        # try to parse & decode data 
        try:         
            parts = data.split(' ')
            if len(parts) > 2 :
                command = parts[0]
                if command == "radio_rx":
                    dataBytes = parts[2]     
                    print("Rx " + str(len(data)) + " bytes: " + str(dataBytes)) 
                    dataStr = zlib.decompress(codecs.decode(dataBytes, "hex")).decode("utf-8")
                    values = dataStr.split(',')
                    sendingCommand = receiveValues(values)  
                    self.send_cmd('radio get snr')  # requires firmware 1.0.5 for RSSI
            else:
                print('INFO: ' + data)
                snr = data  # probably SNR
        except:
            print('ERROR: ' + data)
            logging.error("Exception occurred", exc_info=True)
            return

        self.send_cmd("sys set pindig GPIO10 0", delay=1)
        self.send_cmd('radio rx 0')

        if not sendingCommand == "":
            time.sleep(.3)
            commandBin = zlib.compress(str.encode(sendingCommand)).hex()
            msg = 'radio tx ' + commandBin
            self.send_cmd("sys set pindig GPIO11 1")
            print("SEND: %s bytes " % str(len(commandBin)) + commandBin + " " + sendingCommand)
            self.send_cmd(msg)
            sendingCommand = ""  #clear command
            time.sleep(.5)
            self.send_cmd("sys set pindig GPIO11 0")

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def tx(self, command):
        self.send_cmd("sys set pindig GPIO11 1")
        txmsg = 'radio tx ' + command
        self.send_cmd(txmsg)
        time.sleep(.3)
        self.send_cmd("sys set pindig GPIO11 0")
        #self.frame_count = self.frame_count + 1

    def send_cmd(self, cmd, delay=.5):
        #self.transport.write(('%s\r\n' % cmd).encode('UTF-8'))
        self.write_line(cmd)
        time.sleep(delay)

snr = -99
parser = argparse.ArgumentParser(description='LoRa Radio mode receiver.')
parser.add_argument('--radio', help="Serial port descriptor")
#parser.add_argument('--gps', help="Serial port descriptor")
args = parser.parse_args()

ser = serial.Serial(args.radio, baudrate=57600)
def receive():
        #ser = serial.Serial(args.radio, baudrate=57600)
        with ReaderThread(ser, RxGround) as protocol:
            while(1):
                time.sleep(.1)
                pass        

def sendCommand(command):
    with ReaderThread(ser, RxGround) as protocol:
        protocol.tx(command)

print("Iniitializing LoRa Telemtry...")
telemetry_thread=thread.Thread(target=receive) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()
