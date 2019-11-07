#!/usr/bin/env python3
import time
import traceback
import logging
import telemetry
import telemetrySimulation
import controlPanel

logging.basicConfig(filename='balloon.log', format='%(process)d-%(levelname)s-%(message)s')
logging.info('Initializing Ground Control')

telem = telemetry
telem = telemetrySimulation

def mainloop():
    while not controlPanel.exiting:
        try:
            controlPanel.update(telem.model)
            if not controlPanel.commandToSend == "":
                telem.commandToSend = controlPanel.commandToSend
                controlPanel.commandToSend = ""
            time.sleep(.5)
        except:
            logging.error("app.mainloop(): ", exc_info=True)

mainloop();