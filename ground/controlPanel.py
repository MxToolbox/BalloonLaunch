import sys
sys.path.insert(1, '../common/')
import flightModes
import messages
import tkinter as tk
from tkinter import scrolledtext
import json
from datetime import datetime, timedelta 

commandToSend = ""
lastMessage = 0

def sendCommand(command):
    global commandToSend
    commandToSend = command
    print("Sending: " + command)
    #lbl.configure(text="Tx: " + command.get())

#window.mainloop() is not called.  UI gets updates with this function:
def update(model):
    global app
    global lastMessage
    fmode = flightModes.Modes()
    if model is not None:

        # check for new message
        if not model.Message == lastMessage:        
            app.messageLog.insert(tk.INSERT, str(datetime.now()) + ": " + messages.code[int(model.Message)] + "\r\n")
            lastMessage = model.Message
        
        # Set status indicators
        fmode.SetModeBitArray(model.Mode)
        if fmode.GroundProximity:
            app.GroundProximity.configure(bg="green")
        else:
            app.GroundProximity.configure(bg="grey")
        if fmode.HasGpsFix:
            app.HasGpsFix.configure(bg="green")
        else:
            app.HasGpsFix.configure(bg="grey")
        if fmode.Ascending:
            app.Ascending.configure(bg="green")
        else:
            app.Ascending.configure(bg="grey")
        if fmode.Descending:
            app.Descending.configure(bg="green")
        else:
            app.Descending.configure(bg="grey")                                    
        app.Lbl0.configure(text = model.time)
        #app.TxtArea0.delete(1.0,END)
        #app.TxtArea0.insert(model.__dict__)
        #app.TxtArea0.insert(json.dumps(model.__dict__))
    app.update()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.master.title("MDM-2 Control Panel")
        self.master.geometry('800x600')
        self.hello = tk.Label(self, text="Hello", font=("Arial Bold", 50))
        self.hello.place(x=50,y=700)

        #Use the background color of buttons as status light indicators.
        self.GroundProximity = tk.Button(root, width=15, text='Ground Prox',relief='ridge', fg="white")
        self.HasGpsFix = tk.Button(root, width=15, text='GPS Fix',relief='ridge', fg="white")
        self.Ascending = tk.Button(root, width=15, text='Ascending',relief='ridge', fg="white")
        self.Descending = tk.Button(root, width=15, text='Descending',relief='ridge', fg="white")
        self.GroundProximity.place(x=50,y=10)
        self.HasGpsFix.place(x=150,y=10)
        self.Ascending.place(x=250,y=10)
        self.Descending.place(x=350,y=10)

        #Define buttons and put these in position
        self.BtnSendCommand = tk.Button(root, width=15, text='Send Command!',relief='ridge', fg="white", bg="red", command=self.sendCommand)
        self.Btn1 = tk.Button(root, width=8, text='Quit',relief='ridge',command=self.master.destroy)
        self.Btn2 = tk.Button(root, width=8, text='Left',relief='ridge')
        self.Btn3 = tk.Button(root, width=8, text='Right',relief='ridge')
        self.Btn4 = tk.Button(root, width=8, text='Stop',relief='ridge')
        self.Btn5 = tk.Button(root, width=8, text='Follow',relief='ridge')

        self.Lbl0 = tk.Label(root, text="Hello", font=("Arial Bold", 14))

        self.messageLog = tk.scrolledtext.ScrolledText(root, width=90, height=10)

        self.commandToSend = tk.Entry(root, width=10)

        self.BtnSendCommand.place(x=200,y=150)
        self.Btn1.place(x=100,y=230)
        self.Btn2.place(x=30,y=230)
        self.Btn3.place(x=170,y=230)
        self.Btn4.place(x=170,y=275)
        self.Btn5.place(x=30,y=275)

        self.Lbl0.place(x=50, y=50)
        self.commandToSend.place(x=100, y=150)
        self.messageLog.place(x=25, y=400)

    def sendCommand(self):
        global app
        sendCommand(app.commandToSend.get())

root = tk.Tk()
app = Application(master=root)