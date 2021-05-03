"""Core object for the application. Used for defining application-scope settings."""

import logging
import os
from importlib.metadata import version
from tkinter import font, ttk

from scalewiz.components.log_window import LogWindow
from scalewiz.components.main_frame import MainFrame
from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.logger import Logger


class ScaleWiz(ttk.Frame):
    """Core object for the application."""

    def __init__(self, parent) -> None:
        ttk.Frame.__init__(self, parent)

        # set UI
        # icon / version
        set_icon(parent)
        parent.title(f"ScaleWiz {version('scalewiz')}")
        parent.resizable(0, 0)  # apparently this is a bad practice...
        # but it needs to stay locked for the TestHandlerView's "Toggle details" to work
        # font 🔠
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial")
        parent.option_add("*Font", "TkDefaultFont")
        bold_font = font.Font(family="Helvetica", weight="bold")

        # widget backgrounds / themes 🎨
        parent.tk_setPalette(background="#FAFAFA")
        ttk.Style().configure("TLabel", background="#FAFAFA")
        ttk.Style().configure("TFrame", background="#FAFAFA")
        ttk.Style().configure("TLabelframe", background="#FAFAFA")
        ttk.Style().configure("TLabelframe.Label", background="#FAFAFA")
        ttk.Style().configure("TRadiobutton", background="#FAFAFA")
        ttk.Style().configure("TCheckbutton", background="#FAFAFA")
        ttk.Style().configure("TNotebook", background="#FAFAFA")
        ttk.Style().configure("TNotebook.Tab", font=bold_font)

        # holding a ref to the toplevel for the menubar to find
        self.log_window = LogWindow(Logger())
        logging.getLogger("scalewiz").info("Starting in %s", os.getcwd())
        self.log_window.withdraw()  # 🏌️‍♀️👋
        MainFrame(self).grid()
