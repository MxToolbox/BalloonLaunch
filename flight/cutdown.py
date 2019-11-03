#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import logging
import traceback

CutDownPin = 9    # pin 21 GPIO 9
CutDuration = 5   # number of seconds to energize the hot wire
IsArmed = False

def Energize(IsGroundProximity):
    global CutDownPin
    global IsArmed
    if not (IsGroundProximity):
        logging.warning("CutDown prevented because Ground Proximity was not indicated.")
        return
    if not (IsArmed):
        logging.warning("CutDown prevented because mechanism was not armed.")
        return        
    try:
        logging.warning("Beginning Cutdown!")
        GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
        GPIO.setup(CutDownPin, GPIO.OUT)
        GPIO.output(CutDownPin, GPIO.HIGH)
        time.sleep(CutDuration)
        GPIO.output(CutDownPin, GPIO.LOW)
    except:
        logging.critical("Cutdown error", exc_info=True)
    finally:
        destroy()
        logging.warning("Ending Cutdown!")

def destroy():
	try:
		GPIO.output(CutDownPin, GPIO.HIGH)
		GPIO.cleanup()                     # Release resource
	except:
		logging.error("Cleanup error", exc_info=True)


if __name__ == '__main__':     # Program start from here
	try:
		IsArmed = True
		Energize(True)
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
