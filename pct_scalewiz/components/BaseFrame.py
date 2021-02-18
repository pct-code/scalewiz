import sys
from os import path
import tkinter as tk 
from tkinter import ttk

from models.get_resource import get_resource

class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        # set the Toplevel's icon        
        icon_path = get_resource(r'../../assets/chem.ico') # this makes me nervous, but whatever

        if path.isfile(icon_path):
            self.winfo_toplevel().wm_iconbitmap(icon_path)

  