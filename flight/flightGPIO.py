#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import threading as thread
import logging
import traceback

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
        logging.warning("CutDown prevented because Ground Proximity was not indicated.")
        return
    if not (CutdownArmed):
        logging.warning("CutDown prevented because mechanism was not armed.")
        return        
    try:
        logging.warning("Beginning Cutdown!")
        CutdownInProgress = True
        gpio.setmode(GPIO.BCM) 
        gpio.setup(CutDownPin, GPIO.OUT)
        gpio.output(CutDownPin, GPIO.HIGH)
        time.sleep(CutDuration)
        gpio.output(CutDownPin, GPIO.LOW)
        CutdownInProgress = False
    except:
        logging.critical("Cutdown error", exc_info=True)
    finally:
        #destroy()
        logging.warning("Ending Cutdown!")

def destroy():
    try:
        gpio.output(CutDownPin, GPIO.LOW)
        gpio.output(BuzzerPin, GPIO.LOW)
        gpio.output(CutDownPin, GPIO.LOW)
        gpio.output(BuzzerPin, GPIO.HIGH)     
        gpio.cleanup()                     # Release resource
    except:
        logging.error("Cleanup error", exc_info=True)

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
		logging.error("Exception occurred", exc_info=True)
		destroy()


print("Iniitializing Ground Proxmity Alarm...")
alarm_thread=thread.Thread(target=monitorBuzzer) 
alarm_thread.setDaemon(True)                  
alarm_thread.start()

if __name__ == '__main__':     # Program start from here
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
