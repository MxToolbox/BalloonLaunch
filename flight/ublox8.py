import subprocess
import logging
import time
from datetime import datetime, timedelta 

currentMode = 0
switchOverAlt = 10000
maxAirbroneMinutes = 180  # after this duration, force portable mode as fail-safe.
manualOverride = False
startUpTime = datetime.now()

# Dynamic platform model:
#0: portable
#2: stationary
#3: pedestrian
#4: automotive
#5: sea
#6: airborne with <1g acceleration
#7: airborne with <2g acceleration
#8: airborne with <4g acceleration
#9: wrist worn watch (not supported in

def CheckMode(altMeters):
    global switchOverAlt
    if datetime.now() > startUpTime + timedelta(minutes=maxAirbroneMinutes) and currentMode != 0:
        logging.warning("maxAirbroneMinutes exceeded and currentMode != 0")
        setUbloxDynamicMode(0)  # airborne mode < 1G
    elif altMeters > switchOverAlt and currentMode != 6 and not manualOverride:
        logging.warning("altMeters > switchOverAlt and currentMode != 6")
        setUbloxDynamicMode(6)  # airborne mode < 1G
    elif altMeters < switchOverAlt and currentMode != 0 and not manualOverride:
        logging.warning("altMeters < switchOverAlt and currentMode != 0")
        setUbloxDynamicMode(0)  # portable mode

def IsAirborneMode():
    if currentMode == 6:
        return True
    else:
        return False

def setUbloxDynamicMode(mode, override=False):
    global currentMode
    global manualOverride
    manualOverride = override
    command = "ubxtool -p MODEL -m " + str(mode)
    logging.warning(command)
    proc = subprocess.Popen([command, "/~"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if err is None:
        logging.warning("ubxtool mode change success: " + str(out))
        currentMode = mode
    else:
        logging.warning("ubxtool mode change FAILED: " + str(err))


setUbloxDynamicMode(0)  # initialize to portable mode


if __name__ == '__main__':     # Program test here
    try:
        print("Running UBlox Dynamic mode text.")
        CheckMode(switchOverAlt -1)
        time.sleep(1)
        CheckMode(switchOverAlt +1)
        time.sleep(1)
        CheckMode(switchOverAlt -1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print("Exiting...");    