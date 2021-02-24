import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk

from components.BaseFrame import BaseFrame


class RinseFrame(BaseFrame):
    def __init__(self, handler, window):
        BaseFrame.__init__(self, window)
        window.protocol("WM_DELETE_WINDOW", self.close)
        self.window = window
        self.handler = handler
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.stop = False

        self.winfo_toplevel().title(self.handler.name)

        self.t = tk.IntVar()
        self.t.set(3)
        self.txt = tk.StringVar()
        self.txt.set("Rinse")
        lbl = ttk.Label(window, text="Rinse duration (min).:")
        lbl.grid(row=0, column=0)
        ent = ttk.Spinbox(window, textvariable=self.t, from_=3, to=60)
        ent.grid(row=0, column=1)
        self.button = ttk.Button(
            window, textvariable=self.txt, command=lambda: self.requestRinse()
        )
        self.button.grid(row=2, column=0, columnspan=2)

    def requestRinse(self):
        if not self.handler.isRunning.get() or self.handler.isDone.get():
            self.pool.submit(self.rinse)

    def rinse(self):
        try:
            self.handler.setupPumps()
        except Exception:
            return
        self.handler.pump1.run()
        self.handler.pump2.run()

        self.button.configure(state="disabled")
        duration = self.t.get() * 60
        for i in range(duration):
            if not self.stop:
                self.txt.set(f"{i+1}/{duration} s")
                time.sleep(1)
            else:
                break

        self.terminate()
        self.button.configure(state="normal")

    def terminate(self):
        if self.handler.pump1.port.isOpen():
            self.handler.pump1.stop()
            self.handler.pump1.close()
            # logger.info(f"{self.name}: Stopped and closed the device @ {self.pump1.port.port}")

        if self.handler.pump2.port.isOpen():
            self.handler.pump2.stop()
            self.handler.pump2.close()
            # logger.info(f"{self.name}: Stopped and closed the device @ {self.pump1.port.port}")

    def close(self):
        self.stop = True
        self.window.destroy()
