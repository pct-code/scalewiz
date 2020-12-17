"""Main Window Tkinter widget for the application"""

# util
import tkinter as tk
from tkinter import ttk

# internal
from .MenuBar import MenuBar
from .TestHandlerView import TestHandlerView
from ..models.TestHandler import TestHandler

class MainWindow(tk.Frame):
    """Main Window for the application."""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.root.protocol("WM_DELETE_WINDOW", self.close)
        self.build()

    def build(self) -> None:
        MenuBar(self)  # this will apply itself to the current Toplevel

        self.tabControl = ttk.Notebook(self)
        self.tabControl.grid(sticky='nsew')

        self.addTestHandler()
    
    def addTestHandler(self):
        handler = TestHandler() # make a new handler
        foo = TestHandlerView(self.tabControl, handler) # plug it in
        handler.parent = foo
        self.tabControl.add(foo, sticky=tk.N+tk.W+tk.E+tk.S) # add it to the tab control then rename
        self.tabControl.tab(foo, text=f"  System {self.tabControl.index(foo) + 1}  ") 

    def close(self):
        for tab in self.tabControl.tabs():
            widget = self.nametowidget(tab)
            if widget.handler.isRunning.get():
                if not widget.handler.isDone.get():
                    return
        # todo messagebox saying cant close while running
        self.parent.root.destroy()
        exit()