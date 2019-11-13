import os
import time
from datetime import datetime, timedelta 
import threading as thread


def TimeLapse():
    try:
        LOCATION = os.path.dirname(os.path.abspath(__file__))
        MAXFRAMES = 2000
        TIMEBETWEEN = 10 #seconds
        frameCount = 0
        while frameCount < MAXFRAMES:
            imageFile = LOCATION + "/images/image-" + str(datetime.now()).replace(':', '-').replace(' ', '-') + ".jpg"
            os.system("raspistill -o " + imageFile)
            frameCount += 1
            time.sleep(TIMEBETWEEN - 6) #Takes roughly 6 seconds to take a picture
    except Exception as e:
        logging.error("Raspistills Exception occurred", exc_info=True)

camera_thread=thread.Thread(target=TimeLapse) 
camera_thread.setDaemon(True)                  
camera_thread.start()    
