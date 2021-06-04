"""Simple frame that starts and stops the pumps on a timer."""

import logging
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from tkinter import ttk

from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.test_handler import TestHandler

LOGGER = logging.getLogger("pct-scalewiz")


class RinseWindow(tk.Toplevel):
    """Toplevel control that starts and stops the pumps on a timer."""

    def __init__(self, handler: TestHandler) -> None:
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)
        self.handler: TestHandler = handler
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.stop = False

        set_icon(self)
        self.winfo_toplevel().title(self.handler.name)

        self.rinse_minutes = tk.IntVar()
        self.rinse_minutes.set(5)
        self.txt = tk.StringVar()
        self.txt.set("Rinse")

        # build
        lbl = ttk.Label(self, text="Rinse duration (min).:")
        lbl.grid(row=0, column=0)
        ent = ttk.Spinbox(self, textvariable=self.rinse_minutes, from_=3, to=60)
        ent.grid(row=0, column=1)

        self.button = ttk.Button(self, text="Rinse", command=self.request_rinse)
        self.button.grid(row=2, column=0, columnspan=2)

    def request_rinse(self) -> None:
        """Try to start a rinse cycle if a test isn't running."""
        if self.handler.is_done or not self.handler.is_running:
            self.pool.submit(self.rinse)

    def rinse(self) -> None:
        """Run the pumps and disable the button for the duration of a timer."""
        self.handler.setup_pumps()
        self.handler.pump1.run()
        self.handler.pump2.run()

        self.button.configure(state="disabled")
        duration = round(self.rinse_minutes.get() * 60)
        for i in range(duration):
            if not self.stop:
                self.button.configure(text=f"{i+1}/{duration} s")
                sleep(1)
            else:
                break
        self.bell()
        self.end_rinse()
        self.button.configure(state="normal", text="Rinse")

    def end_rinse(self) -> None:
        """Stop the pumps if they are running, then close their ports."""
        if self.handler.pump1.is_open:
            self.handler.pump1.stop()
            self.handler.pump1.close()
            LOGGER.info(
                "%s: Stopped and closed the device @ %s",
                self.handler.name,
                self.handler.pump1.serial.name,
            )

        if self.handler.pump2.is_open:
            self.handler.pump2.stop()
            self.handler.pump2.close()
            LOGGER.info(
                "%s: Stopped and closed the device @ %s",
                self.handler.name,
                self.handler.pump2.serial.name,
            )

    def close(self) -> None:
        """Stops the rinse cycle and closes the rinse Toplevel."""
        self.stop = True
        self.destroy()
