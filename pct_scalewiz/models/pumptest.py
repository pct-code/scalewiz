import tkinter as tk

from serial import Serial

from pct_scalewiz.models.next_gen_pump import NextGenPump


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.port = tk.StringVar()
        self.port.set("COM3")
        self.build()

    def build(self):
        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.quitButton.grid()

        self.portEntry = tk.Entry(self, textvariable=self.port)
        self.portEntry.grid()

        self.initBtn = tk.Button(self, text="init", command=self.open_port)
        self.initBtn.grid()

        self.ccButton = tk.Button(self, text="reveal", command=self.cc)
        self.ccButton.grid()

        self.redoBtn = tk.Button(self, text="redo", command=self.redo)
        self.redoBtn.grid()

    def open_port(self):
        self.pump = NextGenPump(self.port.get())

    def cc(self):
        print(self.pump.flowrate_factor)
        
    def redo(self):
        self.pump.serial.close()
        del self.pump

app = Application()
app.master.title("Sample application")
app.mainloop()
