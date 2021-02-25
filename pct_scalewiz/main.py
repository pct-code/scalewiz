"""The entry point for the program."""

# utils
import logging
import os
import tkinter as tk
from tkinter import font, ttk

# internal
from pct_scalewiz.components.base_frame import BaseFrame
from pct_scalewiz.components.log_frame import LogFrame
from pct_scalewiz.components.main_frame import MainFrame
from pct_scalewiz.models.logger import Logger


class ScaleWiz(BaseFrame):
    """Core object for the application."""

    def __init__(self, parent):
        # expects the parent to be the root Tk object (and/or it's assoc. toplevel...?)
        BaseFrame.__init__(self, parent)

        # set UI
        # icon / version
        parent.title("")
        parent.resizable(0, 0)  # apparently this is a bad practice...

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

        # make log window, immediately hide it
        # todo this seems inelegant
        # holding a ref for the menubar to find...
        self.log_window = tk.Toplevel(self)
        self.log_window.parent = self  # tacky ?
        LogFrame(self.log_window, Logger()).grid()
        logging.getLogger("scalewiz").info("Starting in %s", os.getcwd())
        self.log_window.withdraw()  # 🏌️‍♀️👋

        MainFrame(self).grid()  # this will hijack the window closing protocol


def main():
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    ScaleWiz(root).grid()
    root.mainloop()


if __name__ == "__main__":
    main()
