from telemetry import Model
import threading as thread
import time
from datetime import datetime, timedelta 
import sys
sys.path.insert(1, '../common/')
import flightModes

values = [0]*32
model = Model(values)

#constants:
model.temp = str(25)
model.humidity = str(14)
model.pressure = str(1013)
model.vertSpeed = str(5)
model.lat = "30.4317"
model.lon = "-97.766"
model.gpsAlt = str(0)
model.gpsSpeed = str(15.0)
model.gpsClimb = str(5.0)
model.gpsTrack = str(360.0)
model.LastFix = str(0.1)
model.snr = str(5)
model.HDOP = str(2)
model.VDOP = str(4)


def Simulate():
    global model
    startTime = datetime.now()
    speedFactor = 360  # number of times faster to run simulation
    missionSeconds = 0 # number of seconds into the simulated mission we are
    BurstAlt = 30000
    hasBurst = False
    fmode = flightModes.Modes()
    fmode.HasGpsFix = True
    verticalSpeed = 5
    while True:
        model.time = startTime + timedelta(seconds=missionSeconds)
        print(model.time)
        if not hasBurst:
                model.pressureAlt = str(int(model.pressureAlt) + verticalSpeed * speedFactor)
                model.gpsAlt = str(int(model.gpsAlt) + verticalSpeed * speedFactor)
                fmode.SetStatus(model.gpsAlt, model.pressureAlt, verticalSpeed)
        elif int(model.pressureAlt) > 0:
                model.pressureAlt = str(int(model.pressureAlt) - verticalSpeed * speedFactor)
                model.gpsAlt = str(int(model.gpsAlt) - verticalSpeed * speedFactor) 
                fmode.SetStatus(model.gpsAlt, model.pressureAlt, verticalSpeed * -1)

        if int(model.pressureAlt) > BurstAlt:
                hasBurst = True
        if int(model.pressureAlt) > int(model.maxAltPessure):             
                model.masAltPessure = model.pressureAlt
                model.gpsAlt = model.gpsAlt
        if fmode.Ascending or fmode.Descending:
                model.lat = round(float(model.lat) + (0.0001 * speedFactor), 4)
                model.lon = round(float(model.lon) + (0.0001 * speedFactor), 4)
        model.Mode = fmode.GetModeBitArray()
        time.sleep(1)
        missionSeconds += speedFactor


telemetry_thread=thread.Thread(target=Simulate) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()
