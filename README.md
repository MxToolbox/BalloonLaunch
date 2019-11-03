# HABTrack-python

## Requirements 

# For SenseHat:
* `sudo apt-get install sense-hat`

# For BMP180:
* `sudo pip3 install smbus`

# For BMP280:
* `sudo pip3 install adafruit-circuitpython-bmp280`

# For ADS1x15 ADC:
* `sudo pip3 install adafruit_ads1x15`

# For GPS / GEO:
* `sudo apt-get install gpsd gpsd-clients python-gps`
* `sudo pip3 install numpy`
* `sudo pip3 install gps`
* `sudo gpsd /dev/serial0 -F /var/run/gpsd.sock`
* `sudo pip3 install geographiclib`

You may need to set your GPS serial port in /etc/defaults/GPSD
Also, gpsctl -[nb] swithes between NEMA and binary for the UBlox M8
Test with cpgs or gpsmon
http://manpages.ubuntu.com/manpages/bionic/man1/gpsctl.1.html

# For LoRa Stik Support:
* `sudo pip3 install serial`
* `sudo pip3 install pySerial`

# Other helpful stuff:
* `sudo apt-get install i2c-tools`  (i2cdetect)
For windows text to speech:  `pip install pyttsx3`

sudo pip install Adafruit_BMP085????

## GPSD?
https://github.com/wb2osz/direwolf/blob/master/doc/Raspberry-Pi-APRS-Tracker.pdf
https://github.com/wb2osz/direwolf.git


# UBlox M8 Commands
/dev/serial0 identified as a u-blox SW ROM CORE 3.01 (107888),HW 00080000,FWVER=SPG 3.01,PROTVER=18 at 9600 baud.

https://ukhas.org.uk/guides:ublox6
https://github.com/SodaqMoja/SodaqOne-UniversalTracker-v3/issues/4
http://manpages.ubuntu.com/manpages/bionic/man1/gpsctl.1.html
https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_%28UBX-13003221%29_Public.pdf

* `gpsctl -f -x "\x06\x24\x01\x00" /dev/serial0`
* `gpsctl -x "\x06\x24\x24\x00\xFF\xFF\x06\x03\x00\x00\x00\x00\x10\x27\x00\x00\x05\x00\xFA\x00\xFA\x00\x64\x00\x2C\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" /dev/serial0`

Full string (with first 2 bytes and last 2 byte checksum)
\xB5\x62\x06\x24\x24\x00\xFF\xFF\x06\x03\x00\x00\x00\x00\x10\x27\x00\x00\x05\x00\xFA\x00\xFA\x00\x64\x00\x2C\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16\xDC