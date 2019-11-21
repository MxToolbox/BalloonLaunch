"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64     # Change to 64 if needed
BORDER = 5

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c, reset=oled_reset)




# Draw Some Text
while True:
    # Clear display.
    oled.fill(0)
    oled.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a white background
    #draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    #draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    #            outline=0, fill=0)

    # Load default font.
    font = ImageFont.load_default()
    #font = ImageFont.truetype("arial.ttf", 15)
    #font = ImageFont.truetype(font=None, size=10, index=0, encoding='')
    text = time.strftime("%H:%M:%S")
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2),
            text, font=font, fill=255)

    # Display image
    oled.image(image)
    oled.show()
    time.sleep(1)
