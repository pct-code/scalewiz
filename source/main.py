"""The entry point for the program.

"""
# utils
import logging
import os
import tkinter as tk
from tkinter import font
from tkinter import ttk

# internal
from app.components.BaseFrame import BaseFrame
from app.components.MainFrame import MainFrame
from app.components.LogFrame import LogFrame
from app.models.Logger import Logger

class App(BaseFrame):
    """Core object for the application."""
    
    VERSION = '[1.0.0]'

    def __init__(self, parent):
        # expects the parent to be the root Tk object (and/or it's assoc. toplevel...?)
        BaseFrame.__init__(self, parent)
        
        # set UI
        # icon / version
        parent.title(f"ScaleWiz {App.VERSION}")
        parent.resizable(0, 0) # apparently this is a bad practice...

        # font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial")
        parent.option_add("*Font", "TkDefaultFont")
        bold_font = font.Font(family="Helvetica", weight='bold')
        
        # widget backgrounds / themes
        parent.tk_setPalette(background='#FAFAFA')
        ttk.Style().configure('TLabel', background='#FAFAFA')
        ttk.Style().configure('TFrame', background='#FAFAFA')
        ttk.Style().configure('TLabelframe', background='#FAFAFA')
        ttk.Style().configure('TLabelframe.Label', background='#FAFAFA')
        ttk.Style().configure('TRadiobutton', background='#FAFAFA')
        ttk.Style().configure('TCheckbutton', background='#FAFAFA')
        ttk.Style().configure('TNotebook', background='#FAFAFA')
        ttk.Style().configure('TNotebook.Tab', font=bold_font)
        
        
        # make log window, immediately hide it
        # holding a ref for the menubar to find...
        self.log_window = tk.Toplevel(self)
        self.log_window.parent = self
        LogFrame(self.log_window, Logger()).grid()
        self.log_window.withdraw()

        MainFrame(self).grid() # this will hijack the window closing protocol
        

if __name__ == "__main__":
    root = tk.Tk()
    App(root).grid()
    root.mainloop()