"""The entry point for the program.

"""
# utils
import os
import tkinter as tk
from tkinter import font
from tkinter import ttk

# internal
from app.components.MainWindow import MainWindow

class App(tk.Frame):
    """Core object for the application."""
    
    VERSION = '[1.0.0]'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # set UI
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial")
        parent.option_add("*Font", "TkDefaultFont")
        bold_font = font.Font(family="Helvetica", weight='bold')
        parent.tk_setPalette(background='#FAFAFA')
        ttk.Style().configure('TLabel', background='#FAFAFA')
        ttk.Style().configure('TFrame', background='#FAFAFA')
        ttk.Style().configure('TLabelframe', background='#FAFAFA')
        ttk.Style().configure('TLabelframe.Label', background='#FAFAFA')
        ttk.Style().configure('TRadiobutton', background='#FAFAFA')
        ttk.Style().configure('TCheckbutton', background='#FAFAFA')
        ttk.Style().configure('TNotebook', background='#FAFAFA')
        ttk.Style().configure('TNotebook.Tab', font=bold_font)

        parent.resizable(0, 0)
        parent.title(f"ScaleWiz {App.VERSION}")
        icon_path = os.path.abspath(r"C:\Users\P\source\repos\scalewiz\assets\chem.ico")
        parent.wm_iconbitmap(icon_path)

        self.root = parent
        
        MainWindow(self).grid()
        # other logic here

if __name__ == "__main__":
    root = tk.Tk()
    App(root).grid()
    root.mainloop()