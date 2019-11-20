import I2C_LCD_driver
import time


mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string("Hello World!", 1, 0)
mylcd.lcd_display_string("Is Bob your uncle?", 2, 0)
mylcd.lcd_display_string("1..2..3..", 3, 0)
mylcd.lcd_display_string("Contact!", 4, 0)

while True:
    try:
        mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M:%S"), 4)
    except:
        print("Exception")
        mylcd = I2C_LCD_driver.lcd()
    time.sleep(1)
mylcd.lcd_clear()