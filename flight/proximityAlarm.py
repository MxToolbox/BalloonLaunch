#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import threading as thread
import logging
import traceback
import math

BuzzerPin = 27    # pin13  GPIO 27
IsGroundAlarm = False

def setup(pin):
	global BuzzerPin
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
	GPIO.setup(BuzzerPin, GPIO.OUT)
	GPIO.output(BuzzerPin, GPIO.LOW)
	time.sleep(.1)
	GPIO.output(BuzzerPin, GPIO.HIGH)

def beep(x):
	global BuzzerPin
	GPIO.output(BuzzerPin, GPIO.LOW)
	time.sleep(x)
	GPIO.output(BuzzerPin, GPIO.HIGH)
	time.sleep(x)

def destroy():
	try:
		GPIO.output(BuzzerPin, GPIO.HIGH)
		GPIO.cleanup()                     # Release resource
	except:
		msg = "Cleanup error?s"

def monitorAlarm():
	global BuzzerPin
	global IsGroundAlarm
	try:
		while True:
			
			if IsGroundAlarm:
				setup(BuzzerPin)
				beep(.1)
				destroy()
			else:
				time.sleep(.1)
	except:
		logging.error("Exception occurred", exc_info=True)
		destroy()

print("Iniitializing Ground Proxmity Alarm...")
alarm_thread=thread.Thread(target=monitorAlarm) 
alarm_thread.setDaemon(True)                  
alarm_thread.start()
# IsGroundAlarm = True for testing.


if __name__ == '__main__':     # Program start from here
	try:
		IsGroundAlarm = True
		monitorAlarm()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
