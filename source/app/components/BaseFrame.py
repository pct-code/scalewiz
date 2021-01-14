import os
import tkinter as tk 
from tkinter import ttk

class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        # set the Toplevel's icon        
        icon_path = os.path.abspath(r"assets/chem.ico")
        if os.path.isfile(icon_path):
            self.winfo_toplevel().wm_iconbitmap(icon_path)
