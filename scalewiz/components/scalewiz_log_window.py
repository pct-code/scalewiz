"""A Toplevel with a ScrolledText. Displays messages from a Logger."""

from __future__ import annotations

import tkinter as tk
from queue import Empty
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING

from scalewiz.helpers.set_icon import set_icon

if TYPE_CHECKING:
    from logging import LogRecord

    from scalewiz.components.scalewiz import ScaleWiz


# thanks https://github.com/beenje/tkinter-logging-text-widget


class LogWindow(tk.Toplevel):
    """A Toplevel with a ScrolledText. Displays messages from a Logger."""

    def __init__(self, core: ScaleWiz) -> None:
        tk.Toplevel.__init__(self)
        self.log_queue = core.log_queue
        self.title("Log Window")
        # replace the window closing behavior with withdrawing instead 🐱‍👤
        self.protocol("WM_DELETE_WINDOW", lambda: self.winfo_toplevel().withdraw())
        self.build()

    def build(self) -> None:
        """Builds the UI."""
        set_icon(self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrolled_text = ScrolledText(self, state="disabled", width=88)
        self.scrolled_text.grid(row=0, column=0, sticky="nsew")
        self.scrolled_text.tag_config("INFO", foreground="black")
        self.scrolled_text.tag_config("DEBUG", foreground="gray")
        self.scrolled_text.tag_config("WARNING", foreground="orange")
        self.scrolled_text.tag_config("ERROR", foreground="red")
        self.scrolled_text.tag_config("CRITICAL", foreground="red", underline=1)
        # start polling messages from the queue 📩
        self.after(100, self.poll_log_queue)

    def poll_log_queue(self) -> None:
        """Checks every 100ms if there is a new message in the queue to display."""
        while True:
            try:
                record = self.log_queue.get(block=False)
            except Empty:
                break
            else:
                self.display(record)
        self.after(100, self.poll_log_queue)

    def display(self, record: LogRecord) -> None:
        """Displays a message in the log."""
        msg = record.getMessage()
        self.scrolled_text.configure(state="normal")
        self.scrolled_text.insert(
            "end", "".join((msg, "\n")), record.levelname
        )  # last arg is for the tag
        self.scrolled_text.configure(state="disabled")
        self.scrolled_text.yview("end")  # scroll to bottom
