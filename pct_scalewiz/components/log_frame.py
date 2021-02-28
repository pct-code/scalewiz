"""A Toplevel with a ScrolledText. Displays messages from a Logger."""

# util
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# internal
from pct_scalewiz.components.base_frame import BaseFrame
from pct_scalewiz.models.logger import Logger

# thanks https://github.com/beenje/tkinter-logging-text-widget


class LogFrame(BaseFrame):
    """A Toplevel with a ScrolledText. Displays messages from a Logger."""

    # expects parent to be a toplevel window
    def __init__(self: BaseFrame, parent: tk.Toplevel, logger: Logger) -> None:
        BaseFrame.__init__(self, parent)
        self.winfo_toplevel().title("Log Window")
        # replace the window closing behavior with withdrawing instead 🐱‍👤
        self.winfo_toplevel().protocol(
            "WM_DELETE_WINDOW", lambda: self.winfo_toplevel().withdraw()
        )
        self.log_queue = logger.log_queue
        self.build()

    def build(self) -> None:
        """Builds the UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrolled_text = ScrolledText(self, state="disabled", width=80)
        self.scrolled_text.grid(row=0, column=0, sticky="nsew")
        self.scrolled_text.tag_config("INFO", foreground="black")
        self.scrolled_text.tag_config("DEBUG", foreground="gray")
        self.scrolled_text.tag_config("WARNING", foreground="orange")
        self.scrolled_text.tag_config("ERROR", foreground="red")
        self.scrolled_text.tag_config("CRITICAL", foreground="red", underline=1)

        # start polling messages from the queue 📩
        self.after(100, self.poll_log_queue)

    def display(self, record) -> None:
        """Displays a message in the log."""
        msg = record.getMessage()
        self.scrolled_text.configure(state="normal")
        self.scrolled_text.insert(
            tk.END, msg + "\n", record.levelname
        )  # last arg is for the tag
        self.scrolled_text.configure(state="disabled")
        self.scrolled_text.yview(tk.END)  # scroll to bottom

    def poll_log_queue(self) -> None:
        """Checks every 100ms if there is a new message in the queue to display."""
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.after(100, self.poll_log_queue)
