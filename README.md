# BalloonLaunch

## Requirements

`sudo apt-get install sense-hat`


## GPSD?
https://github.com/wb2osz/direwolf/blob/master/doc/Raspberry-Pi-APRS-Tracker.pdf
https://github.com/wb2osz/direwolf.git

* `sudo apt-get install gpsd gpsd-clients python-gps`
* `sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock`

On windows, install pywin32 to get access to API for GPS:
`pip install pywin32`