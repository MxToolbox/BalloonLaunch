import os
import csv
from datetime import datetime, timedelta 

LOCATION = os.path.dirname(os.path.abspath(__file__))
LOG_FREQ_SECONDS = 15

lastFileWrite = datetime.now() - timedelta(seconds=LOG_FREQ_SECONDS)
logFile = LOCATION + "/logs/flight-data-" + str(datetime.now()).replace(':', '-') + ".csv"
#logFile = LOCATION + '\\logs\\flight-data-' + str(datetime.now()).replace(':', '-') + ".csv"

eventLogfile = LOCATION + "/event-log.csv"   
trackFile = LOCATION + "/logs/track-data-" + str(datetime.now()) + ".csv"

def writeCsvLog(*args): 
    global logFile
    global lastFileWrite
    
    with open(logFile, mode='a') as results_file:
        # ignore data under the logging frequency limit
        if datetime.now() > lastFileWrite + timedelta(seconds=LOG_FREQ_SECONDS):
            results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            results_writer.writerow(*args)    
            lastFileWrite = datetime.now()

def writeCsvEventLog(value1,value2, message):
    global eventLogfile
    with open(eventLogfile, mode='a') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow([datetime.now(), value1, value2, message])  

def writeCsvTrackData(lat, lon):
    global trackFile
    with open(trackFile, mode='a') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow([datetime.now(), lat, lon])       