import pyttsx3
import time
import threading as thread
class _TTS:
        engine = None
        rate = None
        def __init__(self):
                self.engine = pyttsx3.init()

        def start(self,text_):
                self.engine.setProperty('rate', 200)
                voices = self.engine.getProperty('voices')       #getting details of current voice
                #self.engine.setProperty('voice', voices[0].id)   #male
                self.engine.setProperty('voice', voices[1].id)    #female
                self.engine.say(text_)
                self.engine.runAndWait()

CurrentMessage = "Initializing Your Uncle, Bob"

def wacthForMessage():
        global CurrentMessage
        while (1):
                if CurrentMessage != "":
                        # this wrapper is for strange Python3.7 bug
                        # that only allow the first message to be played.
                        tts = _TTS()
                        tts.start(CurrentMessage)
                        del(tts)
                        CurrentMessage = ""
                else:
                        time.sleep(.1)

voice_thread=thread.Thread(target=wacthForMessage) 
voice_thread.setDaemon(True)                  
voice_thread.start()
