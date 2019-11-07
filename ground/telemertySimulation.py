import telemetry.model as model
import threading as thread
import time
from datetime import datetime, timedelta 



curModel = model()

#constants:
curModel.temp = 25
curModel.humidity = 14
curModel.pressure = 1013
curModel.vertSpeed = 5
curModel.lat = "30.4317"
curModel.lon = "-97.766"
curModel.gpsSpeed = 15.0
curModel.gpsClimb = 5.0
curModel.gpsTrack = 360.0


def Simulate():
    global curModel
    startTime = datetime.now()
    speedFactor = 1  # number of times faster to run simulation
    missionSeconds = 0 # number of seconds into the simulated mission we are
    BurstAlt = 30000
    hasBurst = False
    while True:
        curModel.time = startTime + timedelta(seconds=missionSeconds)
        if not BurstAlt:
                curModel.pressureAlt += 5 * speedFactor  
                curModel.gpsAlt += 5 * speedFactor 
        else:    
                curModel.pressureAlt -= 5 * speedFactor 
                curModel.gpsAlt -= 5 * speedFactor 
        if curModel.pressureAlt > BurstAlt:
                hasBurst = True
        if curModel.pressureAlt > curModel.masAltPessure:             
                curModel.masAltPessure = curModel.pressureAlt
                curModel.gpsAlt = curModel.gpsAlt

        time.sleep(1)
        missionSeconds += speedFactor


telemetry_thread=thread.Thread(target=Simulate) 
telemetry_thread.setDaemon(True)                  
telemetry_thread.start()
