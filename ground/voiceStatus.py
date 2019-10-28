import time
import threading as thread
import pyttsx3

engine = pyttsx3.init()  # text to speech
engine.say("Initializing Ground Control")

def voiceWatcher():
    global engine
    try:
        while (1):
            engine.runAndWait()
            print("Speaking")
            time.sleep(.1)
    except:
        print("Error in voiceWatcher")
   
Voice_thread=thread.Thread(target=voiceWatcher) 
Voice_thread.setDaemon(True)                  
Voice_thread.start()
