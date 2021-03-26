import tkinter as tk

from serial import Serial


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.port = tk.StringVar()
        self.serial = None
        self.build()

    def build(self):
        self.quitButton = tk.Button(self, text="Quit", command=self.quit)
        self.quitButton.grid()

        self.portEntry = tk.Entry(self, textvariable=self.port)
        self.portEntry.grid()

        self.initBtn = tk.Button(self, text="init", command=self.open_port)
        self.initBtn.grid()

        self.ccButton = tk.Button(self, text="cc", command=self.cc)
        self.ccButton.grid()

    def open_port(self):
        self.serial = Serial(self.port.get())
        print(self.serial)

    def cc(self):
        self.serial.write("CC\r".encode())
        print(self.serial.read_until("/".encode()).decode())


app = Application()
app.master.title("Sample application")
app.mainloop()
