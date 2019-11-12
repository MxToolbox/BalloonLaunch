import Adafruit_ADS1x15
import time
import traceback
import logging

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

GAIN = 1
Vin = 5.0
REF_RESISTANCE = 1000

AdConverter1 = Adafruit_ADS1x15.ADS1115()  # Create an ADS1115 ADC (16-bit) instance.

def readVoltage(channel, factor = 1):
    # factor is optional, use this if input is voltage divided (e.g. x5)
    try:
        raw = AdConverter1.read_adc(channel, gain=GAIN)
        Vout = round(((raw / 32768) * 4.096) * factor, 4)
        return Vout
    except:
        logging.error("Exception occurred", exc_info=True)


if __name__ == '__main__':     # Program start from here
    try:
        while True:
            print(readVoltage(0))
            time.sleep(1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print("Exiting...");


