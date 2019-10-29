#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import threading as thread
import math

BuzzerPin = 13    # pin15
IsGroundAlarm = False

def setup(pin):
	global BuzzerPin
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
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
			setup(BuzzerPin)
			if IsGroundAlarm:
				beep(.1)
			else:
				destroy()
			time.sleep(.1)
	except:
		destroy()

print("Iniitializing Ground Proxmity Alarm...")
alarm_thread=thread.Thread(target=monitorAlarm) 
alarm_thread.setDaemon(True)                  
alarm_thread.start()


if __name__ == '__main__':     # Program start from here
	try:
		IsGroundAlarm = True
		monitorAlarm()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
