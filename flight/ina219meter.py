import logging
from time import sleep
from ina219 import INA219

isFound = False

try:
    ina = INA219(shunt_ohms=0.1,
             max_expected_amps = 0.6,
             address=0x40)

    ina.configure(voltage_range=ina.RANGE_16V,
              gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_128SAMP,
              shunt_adc=ina.ADC_128SAMP)
    isFound = True
except OSError:
    logging.info('INA219 Not Found')


def voltage():
    if (isFound):
        return ina.voltage()
    else:
        return 0

def current(): 
    if (isFound):
        return ina.current()
    else:
        return 0

def power():
    if (isFound):
        return ina.power()
    else:
        return 0      

#lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
#                       cols=16, lines=2)

if __name__ == '__main__':     # Program start from here
    try:
        while True:
            v = ina.voltage()
            i = ina.current()
            p = ina.power()
            #lcd.clear()
            #lcd.message('{0:0.1f}V {1:0.1f}mA'.format(v, i))
            #lcd.message('\n{0:0.1f} Watts'.format(p/1000))
            print('{0:0.1f}V {1:0.1f}mA'.format(v, i))
            sleep(1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print("Exiting...")
