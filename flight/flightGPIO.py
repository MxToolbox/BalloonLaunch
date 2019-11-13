#!/usr/bin/env python3
import sys
sys.path.insert(1, '../common/')
import RPi.GPIO as GPIO
import time
import threading as thread
import logging
import traceback
import messages

IsGroundAlarm = False
CutdownArmed = False

CutdownInProgress = False

gpio = GPIO

CutDownPin = 9    # pin 21 GPIO 9
BuzzerPin = 27    # pin13  GPIO 27
CutDuration = 30   # number of seconds to energize the hot wire


def CutDownEnergize(IsGroundProximity):
    global CutDownPin
    global CutdownArmed
    global CutdownInProgress
    if not (IsGroundProximity):
        # CutDown prevented because Ground Proximity was not indicated.
        logging.warning(messages.code[460])
        return 460
    if not (CutdownArmed):
        # CutDown prevented because mechanism was not armed.
        logging.warning(messages.code[461])
        return 461      
    try:
        logging.warning("Beginning Cutdown!")
        CutdownInProgress = True
        gpio.setmode(GPIO.BCM) 
        gpio.setup(CutDownPin, GPIO.OUT)
        gpio.output(CutDownPin, GPIO.HIGH)
        time.sleep(CutDuration)
        gpio.output(CutDownPin, GPIO.LOW)
        CutdownInProgress = False
        logging.warning("Ending Cutdown!")
        # Cutdown command executed OK.
        logging.warning(messages.code[260])
        return 260              
    except:
        # CutDown Error.
        logging.warning(messages.code[560])
        return 560     


def destroy():
    try:
        gpio.output(CutDownPin, GPIO.LOW)
        gpio.output(BuzzerPin, GPIO.LOW)
        gpio.output(CutDownPin, GPIO.LOW)
        gpio.output(BuzzerPin, GPIO.HIGH)     
        gpio.cleanup()                     # Release resource
    except:
        logging.error("flightGPIO Cleanup error", exc_info=True)

def beep():
    global BuzzerPin
    global CutdownInProgress
    duration = .1
    if CutdownInProgress:
        duration = 1  # long beep during cutdown
    gpio.setmode(GPIO.BCM) 
    gpio.setup(BuzzerPin, GPIO.OUT)
    gpio.output(BuzzerPin, GPIO.LOW)
    time.sleep(duration)
    gpio.output(BuzzerPin, GPIO.HIGH)
    time.sleep(duration)

def monitorBuzzer():
	global BuzzerPin
	global IsGroundAlarm
	try:
		while True:			
			if IsGroundAlarm:
				beep()
			else:
				time.sleep(.1)
	except:
		logging.error("flightGPIO Exception occurred", exc_info=True)
		destroy()

print("Iniitializing Ground Proxmity Alarm...")
logging.info("Iniitializing Ground Proxmity Alarm...")
alarm_thread=thread.Thread(target=monitorBuzzer) 
alarm_thread.setDaemon(True)                  
alarm_thread.start()

if __name__ == '__main__':     # Test start from here
    try:
        #setup()
        IsGroundAlarm = True
        time.sleep(1)
        CutdownArmed = True
        CutDownEnergize(True)
        IsGroundAlarm = True
        destroy()        
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
    except:
        destroy()
