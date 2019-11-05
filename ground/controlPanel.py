import tkinter as tk
from tkinter import scrolledtext
import json


def sendCommand():
    pass
    #lbl.configure(text="Tx: " + command.get())

#window.mainloop() is not called.  UI gets updates with this function:
def updateTelemetry(model):
    global app
    if app is not None:
        app.Lbl0.configure(text = model.time)
        #app.TxtArea0.delete(1.0,END)
        #app.TxtArea0.insert(json.dumps(model.__dict__))
        app.TxtArea0.insert(json.dumps(model.__dict__))
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
        self.hello.place(x=10,y=10)
        #Define buttons and put these in position
        self.Btn0 = tk.Button(root, width=8, text='CutDown!',relief='ridge', fg="red", command=self.sendCommand)
        self.Btn1 = tk.Button(root, width=8, text='Quit',relief='ridge',command=self.master.destroy)
        self.Btn2 = tk.Button(root, width=8, text='Left',relief='ridge')
        self.Btn3 = tk.Button(root, width=8, text='Right',relief='ridge')
        self.Btn4 = tk.Button(root, width=8, text='Stop',relief='ridge')
        self.Btn5 = tk.Button(root, width=8, text='Follow',relief='ridge')

        self.Lbl0 = tk.Label(root, text="Hello", font=("Arial Bold", 14))

        self.TxtArea0 = tk.scrolledtext.ScrolledText(root, width=40, height=10)

        self.commandToSend = tk.Entry(root, width=10)

        self.Btn0.place(x=100,y=195)
        self.Btn1.place(x=100,y=230)
        self.Btn2.place(x=30,y=230)
        self.Btn3.place(x=170,y=230)
        self.Btn4.place(x=170,y=275)
        self.Btn5.place(x=30,y=275)

        self.Lbl0.place(x=50, y=50)
        self.TxtArea0.place(x=50, y=300)

    def sendCommand(self):
        pass

root = tk.Tk()
app = Application(master=root)