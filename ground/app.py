#!/usr/bin/env python3
import time
import traceback
import logging
import telemetry
#import telemertySimulation
import controlPanel
#import voiceStatus
#voice.CurrentMessage = statusMessage

logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Initializing Ground Control')

Telemetry = telemetry
#telem = telemertySimulation

def mainloop():
    print("Starting...")
    while not controlPanel.exiting:
        try:
            controlPanel.update(Telemetry.model)
            if not controlPanel.commandToSend == "":
                Telemetry.commandToSend = controlPanel.commandToSend
                controlPanel.commandToSend = ""
            time.sleep(.5)
        except:
            logging.error("app.mainloop(): ", exc_info=True)

mainloop()