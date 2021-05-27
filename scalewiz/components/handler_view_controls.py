from __future__ import annotations

import tkinter as tk
from logging import Logger, getLogger
from queue import Empty
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
        self.build()

    def build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # row 0 col 0
        start_btn = ttk.Button(self)
        if self.handler.is_done and not self.handler.is_running:
            start_btn.configure(text="New", command=self.handler.new_test)
        elif self.handler.is_running and not self.handler.is_done:
            start_btn.configure(
                text="New", command=self.handler.new_test, state="disabled"
            )
        else:
            start_btn.configure(text="Start", command=self.handler.start_test)
        start_btn.grid(row=0, column=0, sticky="ew")
        # row 0 col 1
        if self.handler.is_running:
            state = "normal"
        else:
            state = "disabled"
        stop_btn = ttk.Button(
            self, text="Stop", command=self.handler.request_stop, state=state
        )
        stop_btn.grid(row=0, column=1, sticky="ew")
        progressbar = ttk.Progressbar(self, variable=self.handler.progress, maximum=100)
        progressbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        # row 1 col 0:1
        self.log_text = ScrolledText(
            self, background="white", height=5, width=44, state="disabled"
        )
        self.log_text.grid(row=2, column=0, columnspan=2, sticky="ew")
        # enter polling loop
        self.after(0, self.poll_log_queue)

    def poll_log_queue(self) -> None:
        """Checks on an interval if there is a new message in the queue to display."""
        try:
            record = self.handler.log_queue.get(block=False)
        except Empty:
            pass
        else:
            self.display(record)
        self.after(self.interval, self.poll_log_queue)

    def display(self, msg: str) -> None:
        """Displays a message in the log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "".join((msg, "\n")))
        self.log_text.configure(state="disabled")
        self.log_text.yview("end")  # scroll to bottom
