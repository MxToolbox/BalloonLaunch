import sys
import logging
import math
sys.path.insert(1, '../common/')
import flightModes
import messages
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import json
from datetime import datetime, timedelta 
import webbrowser

telemModel = None
def openMapsLink():
    global telemModel
    url = "http://maps.google.com/?q=" + str(telemModel.lat) + "," + str(telemModel.lon)
    print(url)
    webbrowser.open_new(url)

commandToSend = ""
exiting = False
lastMessage = 0
lastRxTime = datetime.now()

def sendCommand(command):
    global commandToSend
    commandToSend = command
    print("Sending: " + command)
    #lbl.configure(text="Tx: " + command.get())

#window.mainloop() is not called.  UI gets updated with this function:
def update(model):
    global app
    global lastMessage
    global lastRxTime
    global telemModel
    telemModel = model
    
    if model is not None:
        lastRxTime = model.modelCreated # datetime.strptime(model.time, '%Y-%m-%d %H:%M:%S.%f')
        lastRxSeconds = int((datetime.now() - lastRxTime).total_seconds())  #LastPacket (seconds since)
        app.lastRx.configure(text="Last Rx (s): " + str(lastRxSeconds))
        try:
            # check for new message
            if not model.Message == lastMessage:        
                app.messageLog.insert(tk.INSERT, str(datetime.now()) + ": " + messages.code[int(model.Message)] + "\r\n")
                lastMessage = model.Message

            setStatusIndicators(app, model)


            app.gpsAlt.configure(text = "Altitude:  " + model.gpsAlt + " m  " + model.vertSpeed + " m/s")
            app.position.delete(0, tk.END)
            app.position.insert(0, str(model.lat) + " , " + str(model.lon))     
            
            # \u2103  degrees C
            try:
                app.gpsSpeed.configure(text = "Tracking: " + str(int(float(model.gpsTrack))) + "\u00B0 at " + str(int(float(model.gpsSpeed))) + " m/s")

            except:
                pass
            app.bearing.configure(text = "Bearing " +  str(int(float(model.heading))) + "\u00B0 at " + str(int(float(model.losRange))) + " m, Elevation " + str(int(float(model.elevation))) + "\u00B0 ")

        except:
            logging.error("controlPanel.update(): ", exc_info=True)
            app.messageLog.insert(tk.INSERT, "Control Panel Error\r\n")

    app.update()

def setStatusIndicators(app, model):
    # Set status indicators
    fmode = flightModes.Modes()
    fmode.SetModeBitArray(model.Mode)
    if fmode.GroundProximity:
        app.GroundProximity.configure(bg="green")
    else:
        app.GroundProximity.configure(bg="grey")
    
    if fmode.HasGpsFix:
        if round(float(model.HDOP),1) < 5:
            app.HasGpsFix.configure(bg="green", fg="white", text = "GPS Fix: " + str(round(float(model.HDOP),1)) + "/" + str(round(float(model.VDOP),1)))
        else:
            app.HasGpsFix.configure(bg="yellow", fg="black" , text = "GPS Fix: " + str(round(float(model.HDOP),1)) + "/" + str(round(float(model.VDOP),1)))
    else:
        app.HasGpsFix.configure(bg="red", fg="white", text = "Last GPS Fix " + model.LastFix + " min")
    
    if fmode.Ascending:
        app.Ascending.configure(bg="green", text = "Ascending " + model.vertSpeed + " m/s")
    else:
        app.Ascending.configure(bg="grey", fg="white", text = "Ascending")
    
    if fmode.Descending:
        app.Descending.configure(bg="yellow", fg="black", text = "Descending " + model.vertSpeed + " m/s")
    else:
        app.Descending.configure(bg="grey", fg="white", text = "Descending")                                    
    
    if str.isnumeric(model.snr):
        if int(model.snr) > 0:
            app.SNR.configure(bg="green", fg="white", text = "SNR: " + model.snr)
        elif int(model.snr) > -4:
            app.SNR.configure(bg="yellow", fg="black", text = "SNR: " + model.snr)
        else:
            app.SNR.configure(bg="red",fg="white", text = "SNR: " + model.snr)

    powerLevel = str(model.voltage) + "V / " + str(model.current) + "A / " + str(round(float(model.voltage) * float(model.current),2)) + "W"
    if float(model.voltage) > 11:
        app.Power.configure(bg="green", fg="white", text = powerLevel)
    elif float(model.voltage) > 10:
        app.Power.configure(bg="yellow", fg="black",  text = powerLevel)
    else:
        app.Power.configure(bg="red", fg="white",  text = powerLevel)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.master.title("MDM-2 Control Panel")
        self.master.geometry('1280x800')
        #self.gpsAlt = tk.Label(self, text="0m", font=("Arial Bold", 50))
        #self.gpsAlt.place(x=50,y=700)

        #Use the background color of buttons as status light indicators.
        self.GroundProximity = tk.Button(root, width=24, text='Ground Prox',relief='ridge', fg="white", font=("Courier Bold", 12))
        self.HasGpsFix = tk.Button(root, width=24, text='GPS Fix',relief='ridge', fg="white", font=("Courier Bold", 12))
        self.Ascending = tk.Button(root, width=24, text='Ascending',relief='ridge', fg="white", font=("Courier Bold", 12))
        self.Descending = tk.Button(root, width=24, text='Descending',relief='ridge', fg="white", font=("Courier Bold", 12))
        self.SNR = tk.Button(root, width=24, text='SNR',relief='ridge', fg="white", font=("Courier Bold", 12))        
        self.Power = tk.Button(root, width=24, text='Power',relief='ridge', fg="white", font=("Courier Bold", 12))
        self.GroundProximity.place(x=50,y=10)
        self.HasGpsFix.place(x=250,y=10)
        self.Ascending.place(x=450,y=10)
        self.Descending.place(x=650,y=10)
        self.SNR.place(x=850,y=10)
        self.Power.place(x=1050,y=10)

        #Define and put these in position

        self.gpsAlt = tk.Label(root, text="0m", font=("Arial Bold", 14))
        self.gpsAlt.place(x=50, y=50)

        self.gpsSpeed = tk.Label(root, text="0m", font=("Arial Bold", 14))
        self.gpsSpeed.place(x=50, y=80)

        self.messageLog = tk.scrolledtext.ScrolledText(root, width=125, height=15, font=("Arial Bold", 12), bg="black", fg="white")
        self.messageLog.place(x=25, y=400)

        self.commandToSend = tk.Entry(root, width=25,font=("Arial Bold", 12))
        self.commandToSend.place(x=400, y=80)
        self.BtnSendCommand = tk.Button(root, width=15, text='Send Command!',relief='ridge', fg="white", bg="red", font=("Courier Bold", 10), command=self.sendCommand)
        self.BtnSendCommand.place(x=600,y=80)

        self.position = tk.Entry(root, width=25,font=("Arial Bold", 12))
        self.position.place(x=400, y=50)

        self.mapsLink = tk.Label(root, text="Google Maps", fg="blue", cursor="hand2")
        self.mapsLink.bind("<Button-1>", lambda e: openMapsLink())
        self.mapsLink.place(x=600, y=50)

        self.bearing = tk.Label(root, text="Bearing ",font=("Arial Bold", 11))
        self.bearing.place(x=50, y=110)

        self.lastRx = tk.Label(root, text="Last Rx ",font=("Arial Bold", 11))
        self.lastRx.place(x=400, y=110)        
        #self.separator = tk.Frame(height=20, bd=1, relief=tk.SUNKEN)
        #self.separator.place(x=50, y=100)



    def on_closing(self):
        global exiting
        #if messagebox.askokcancel("Quit", "Do you want to quit?"):
        exiting = True
        root.destroy()

    def sendCommand(self):
        global app
        sendCommand(app.commandToSend.get())

root = tk.Tk()
app = Application(master=root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)

