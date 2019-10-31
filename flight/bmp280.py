import adafruit_bmp280
import board
import busio
import traceback
import logging

#sensor = {"temperature": 0,"pressure": 0}
sensor = None
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
except:
    logging.error("BMP280 Not Found.  Reporting zero values instead.", exc_info=True)


# To read, just access these two variables:
#sensor.temperature
#sensor.pressure