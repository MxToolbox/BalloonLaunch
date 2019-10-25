# writes CSV log data for flight app

import os
import csv
from datetime import datetime, timedelta 

LOCATION = os.path.dirname(os.path.abspath(__file__))
LOG_FREQ_SECONDS = 15
lastFileWrite = datetime.now() - timedelta(seconds=LOG_FREQ_SECONDS)
logFile = LOCATION + "/logs/flight-data-" + str(datetime.now()).replace(':', '-') + ".csv"

def writeCsvLog(*args): 
    global logFile
    global lastFileWrite
    
    with open(logFile, mode='a') as results_file:
        # ignore data under the logging frequency limit
        if datetime.now() > lastFileWrite + timedelta(seconds=LOG_FREQ_SECONDS):
            results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            results_writer.writerow(*args)    
            lastFileWrite = datetime.now()
     