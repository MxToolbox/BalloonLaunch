import board
import busio
import adafruit_bmp280

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# To read, just access these two variables:
#sensor.temperature
#sensor.pressure