import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):

        self.hello = tk.Label(self, text="Hello", font=("Arial Bold", 50))
        self.hello.place(x=10,y=10)
        #Define buttons and put these in position
        self.Btn0 = tk.Button(root, width=8, text='CutDown!',relief='ridge', fg="red", command=self.cutdown)
        self.Btn1 = tk.Button(root, width=8, text='Quit',relief='ridge',command=self.master.destroy)
        self.Btn2 = tk.Button(root, width=8, text='Left',relief='ridge')
        self.Btn3 = tk.Button(root, width=8, text='Right',relief='ridge')
        self.Btn4 = tk.Button(root, width=8, text='Stop',relief='ridge')
        self.Btn5 = tk.Button(root, width=8, text='Follow',relief='ridge')

        self.Btn0.place(x=100,y=195)
        self.Btn1.place(x=100,y=230)
        self.Btn2.place(x=30,y=230)
        self.Btn3.place(x=170,y=230)
        self.Btn4.place(x=170,y=275)
        self.Btn5.place(x=30,y=275)

    def cutdown(self):
        print("Cutdown!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()