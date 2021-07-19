from __future__ import annotations

import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from logging import Logger, getLogger
from queue import Empty
from time import sleep, time
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scalewiz.models.test_handler import TestHandler


LOGGER: Logger = getLogger("scalewiz")


class TestControls(ttk.Frame):
    """A widget for selecting devices."""

    def __init__(self, parent: tk.Widget, handler: TestHandler) -> None:
        super().__init__(parent)
        self.handler: TestHandler = handler
        self.interval: int = round(handler.project.interval_seconds.get() * 1000)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.stop = tk.BooleanVar()
        self.stop.set(True)
        # todo get this from project settings
        self.rinse_minutes = tk.IntVar()
        self.rinse_minutes.set(5)
        self.build()

    def make_start_btn(self) -> None:
        if self.handler.is_done and not self.handler.is_running:
            self.start_btn.configure(text="New", command=self.handler.new_test)
        elif self.handler.is_running and not self.handler.is_done:
            self.start_btn.configure(
                text="New", command=self.handler.new_test, state="disabled"
            )
        else:  # not running and not done
            self.start_btn.configure(text="Start", command=self.handler.start_test)

    def build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.start_btn = ttk.Button(self)
        self.start_btn.grid(row=0, column=0, sticky="ew")
        self.make_start_btn()
        # row 0 col 0
        self.start_btn = ttk.Button(self)
        if self.handler.is_done and not self.handler.is_running:
            self.start_btn.configure(text="New", command=self.handler.new_test)
        elif self.handler.is_running and not self.handler.is_done:
            self.start_btn.configure(
                text="New", command=self.handler.new_test, state="disabled"
            )
        else:  # not running and not done
            self.start_btn.configure(text="Start", command=self.handler.start_test)
        self.start_btn.grid(row=0, column=0, sticky="ew")
        # row 0 col 1
        if self.handler.is_running:
            # state = "normal"
            text = "Stop"
            command = self.handler.request_stop
        else:
            # state = "disabled"
            text = "Rinse"
            command = self.request_rinse
        self.stop_btn = ttk.Button(self, text=text, command=command, state="normal")
        self.stop_btn.grid(row=0, column=1, sticky="ew")
        progress_lbl = ttk.Label(
            self, textvariable=self.handler.progress_msg, anchor="center"
        )
        progress_lbl.grid(row=1, columnspan=2, sticky="ew")
        progress_bar = ttk.Progressbar(
            self, variable=self.handler.progress, maximum=100
        )
        progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        # row 1 col 0:1
        self.log_text = ScrolledText(
            self, background="white", height=5, width=44, state="disabled"
        )
        self.log_text.grid(row=3, column=0, columnspan=2, sticky="ew")
        # enter polling loop
        self.after(0, self.poll_log_queue)

    def request_rinse(self) -> None:
        """Try to start a rinse cycle if a test isn't running."""
        if self.handler.is_done or not self.handler.is_running:
            self.stop.set(False)
            self.pool.submit(self.rinse)

    def rinse(self) -> None:
        """Run the pumps and disable the button for the duration of a timer."""
        self.handler.setup_pumps()
        self.handler.pump1.run()
        self.handler.pump2.run()

        self.stop_btn.configure(state="disabled")
        self.start_btn.configure(text="Stop Rinse", command=lambda: self.stop.set(True))
        duration = round(self.rinse_minutes.get() * 60)
        rinse_start = time()

        for i in range(duration):
            if not self.stop.get():
                self.handler.progress.set(round((i + 1) / duration) * 100)
                self.handler.progress_msg.set(f"{i+1}/{duration} s")
                sleep(1 - ((time() - rinse_start) % 1))
            else:
                break
        self.bell()
        self.end_rinse()
        self.stop.set(True)
        self.stop_btn.configure(state="normal", text="Rinse")
        self.make_start_btn()

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

    def poll_log_queue(self) -> None:
        """Checks on an interval if there is a new message in the queue to display."""
        while True:
            try:
                record = self.handler.log_queue.get(block=False)
            except Empty:
                break
            else:
                self.display(record)
        self.after(self.interval, self.poll_log_queue)

    def display(self, msg: str) -> None:
        """Displays a message in the log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "".join((msg, "\n")))
        self.log_text.configure(state="disabled")
        self.log_text.yview("end")  # scroll to bottom
