#!/usr/bin/env python3
import sys
import os
import time
import traceback
import threading as thread
import math
import numpy
import zlib
from geographiclib.geodesic import Geodesic
import logging
import winsound  #windows only
import gpsFileWatcher
import csvLog
from datetime import datetime, timedelta 
sys.path.insert(1, '../common/')
import loraRadio
import flightModes
import voiceStatus
radio = loraRadio
radio.RequestSNR = True
gpsWatcher = gpsFileWatcher
fmode = flightModes.Modes()
voice = voiceStatus

model = None
commandToSend = ""
def monitorTelemetry():
    global radio
    global gpsWatcher
    global fmode
    global voice
    global model
    global commandToSend

    rxPositionSet = False
    rxLat = 30.4316015
    rxLon = -97.7660455
    rxAlt = 800  #feet
    txLat = 0.0
    txLon = 0.0

    headers = ["time","temp","humidity","pressure","pressure alt (m)","vert speed (m/s)","pitch","roll","yaw","compass","lat","lon","gps alt (m)","gps speed (m/s)", "gps climb (m/s)", "gps track", "gps time","maxAltGps (m)","maxAltPressure (ft)", "HDOP", "VDOP", "LastFix", "Mode", "Message", "down range (m)", "heading", "snr", "rx lat", "rx lon", "rx alt", "elevation", "los range (m)"]
    csvLog.writeCsvLog(headers)
    radio.DefaultReceive = True
    # Poll for new data
    while True:
        if radio.ReceivedDataReady:
            # Calc geo range / heading
            try:
                values = radio.ReceivedData.split(',')
                radio.ReceivedData = ""  # clear the data
                radio.ReceivedDataReady = False

                txAlt = round((((1 - (float(values[3]) / 1013.25)** 0.190284)) * 145366.45) / 3.28, 0)  # calc pressure alt from pressure
                values[4] = txAlt  #pressure alt (feet)
                txLat = float(values[10])
                txLon = float(values[11])

                txAltGPS = values[12]
                txClimbGPS = values[14]              
                lastFix = float(values[21])
                
                if (rxPositionSet == False):
                    rxPositionSet = True
                    rxLat = txLat
                    rxLon = txLon
                    rxAlt = txAlt
                    print("Receiver position synced with transmitter position: " + str(rxLat) + ' , ' + str(rxLon) )

                # Decode and output mode status
                fmode.SetModeBitArray(values[22])
                statusMessage = fmode.StatusMessage(txAltGPS,txClimbGPS)
                print(statusMessage)
                voice.CurrentMessage = statusMessage

                rxLat = round(gpsWatcher.latitude,6)  # Geo from local GPS on transer device
                rxLon = round(gpsWatcher.longitude,6)
                rxAlt = int(gpsWatcher.altitude)

                geo = Geodesic.WGS84.Inverse(rxLat, rxLon, txLat, txLon)
                distance = 0
                azimuth = 0
                if math.isnan(rxLat) or math.isnan(rxLon) or math.isnan(txLat)  or math.isnan(txLon) or lastFix > 60.0:
                    msg = "Missing GPS Fix.  Last fix was " + str(round(lastFix/60,1)) + " minutes ago!"
                    print(msg )
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
                values.append(radio.SNR)
                values.append(rxLat)
                values.append(rxLon)
                values.append(rxAlt)
                

                elevation = 0
                los_range = 0
                if distance > 0:
                    altDeltaMeters = txAlt - rxAlt  #txAlt is pressure alt is now in METERS!
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
                    #print(colors[i] ,formatStr.format(headers[i],  v))
                    print(formatStr.format(headers[i],  v))
                    i = i + 1
                print(' _____________________________________________________')
                model = Model(values)
                
                # Set value to send to Flight Computer  (uncomment to test)
                radio.DataToTransmit = commandToSend
                commandToSend = "" # clear command
            except:
                print("Exception")
                logging.error("Exception occurred", exc_info=True)
        else:
            time.sleep(.1)

print("Iniitializing Ground Telemetry...")
alarm_thread=thread.Thread(target=monitorTelemetry) 
alarm_thread.setDaemon(True)                  
alarm_thread.start()  


class Model():
  def __init__(self, dataArray):
    self.dataArray = dataArray

    # these values are transmitted from ballon:
    self.time = self.dataArray[0]
    self.temp = self.dataArray[1]   
    self.humidity = self.dataArray[2]
    self.pressure = self.dataArray[3]
    self.pressureAlt = self.dataArray[4]
    self.vertSpeed = self.dataArray[5]
    self.pitch = self.dataArray[6]
    self.roll = self.dataArray[7]
    self.yaw = self.dataArray[8]
    self.compass = self.dataArray[9]
    self.lat = self.dataArray[10]
    self.lon = self.dataArray[11]
    self.gpsAlt = self.dataArray[12]
    self.gpsSpeed = self.dataArray[13]
    self.gpsClimb = self.dataArray[14]
    self.gpsTrack = self.dataArray[15]
    self.gpsTime = self.dataArray[16]
    self.maxAltGps = self.dataArray[17]
    self.maxAltPessure = self.dataArray[18]
    self.HDOP = self.dataArray[19]
    self.VDOP = self.dataArray[20]
    self.LastFix = self.dataArray[21]
    self.Mode = self.dataArray[22]
    self.Message  = self.dataArray[23]

  # these are dervived locally by the ground app
    self.downRange = 0.0
    self.heading = 0.0
    self.snr = 0
    self.rxLat = 0.0
    self.rxLon = 0.0
    self.rxAlt = 0.0
    self.elevation = 0.0
    self.losRange = 0.0

    if len(self.dataArray) > 24:
      try:
        self.downRange = dataArray[24]
        self.heading = dataArray[25]
        self.snr = dataArray[26]
        self.rxLat = dataArray[27]
        self.rxLon = dataArray[28]
        self.rxAlt = dataArray[29]
        self.elevation = dataArray[30]
        self.losRange = dataArray[31]
      except:
          logging.error("Exception occurred loading telemetry model", exc_info=True)
    self.modelCreated = datetime.now()
