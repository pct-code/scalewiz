"""Core object for the application. Used for defining application-scope settings."""

import logging
import os
from importlib.metadata import version
from logging.handlers import QueueHandler
from queue import Queue
from tkinter import font, ttk

from scalewiz.components.log_window import LogWindow
from scalewiz.components.main_frame import MainFrame
from scalewiz.helpers.set_icon import set_icon


class ScaleWiz(ttk.Frame):
    """Core object for the application.

    Used to define widget styles and set up logging.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        # set UI
        # icon / version
        set_icon(parent)
        parent.title(f"ScaleWiz {version('scalewiz')}")
        parent.resizable(0, 0)  # apparently this is a bad practice...
        # font 🔠
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial")
        parent.option_add("*Font", "TkDefaultFont")
        bold_font = font.Font(family="Helvetica", weight="bold")
        ttk.Style().configure("TNotebook.Tab", font=bold_font)
        # widget backgrounds / themes 🎨
        parent.tk_setPalette(background="#FAFAFA")
        for aspect in ("TLabel", "TFrame", "TRadiobutton", "TCheckbutton", "TNotebook"):
            ttk.Style().configure(aspect, background="#FAFAFA")
        # configure logging functionality
        self.log_queue = Queue()
        queue_handler = QueueHandler(self.log_queue)
        # this is for inspecting the multithreading
        # fmt = (
        #     "%(asctime)s - %(func)s - %(thread)d "
        #     "- %(levelname)s - %(name)s - %(message)s"
        # )
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            fmt,
            date_fmt,
        )
        logging.basicConfig(level=logging.DEBUG)  # applies to the root logger instance
        queue_handler.setFormatter(formatter)
        queue_handler.setLevel(logging.INFO)
        logger = logging.getLogger("scalewiz")
        logger.addHandler(queue_handler)
        # holding a ref to the toplevel for the menubar to find
        self.log_window = LogWindow(self)
        logger.info("Starting in %s", os.getcwd())
        self.log_window.withdraw()  # 🏌️‍♀️👋
        MainFrame(self).grid()
