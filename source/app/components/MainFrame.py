"""Main Window Tkinter widget for the application"""

# util
import logging
import tkinter as tk
from tkinter import ttk

# internal
from .BaseFrame import BaseFrame
from .MenuBar import MenuBar
from .TestHandlerView import TestHandlerView
from ..models.TestHandler import TestHandler

logger = logging.getLogger('scalewiz')

class MainFrame(BaseFrame):
    """Main Frame for the application."""

    def __init__(self, parent):
        BaseFrame.__init__(self, parent)
        # hijack closing protocol
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)
        self.build()

    def build(self) -> None:
        MenuBar(self)  # this will apply itself to the current Toplevel

        self.tabControl = ttk.Notebook(self)
        self.tabControl.grid(sticky='nsew')
        self.addTestHandler()
    
    def addTestHandler(self):
        # make a new handler
        handler = TestHandler() 
        system_name = f"  System {len(self.tabControl.tabs()) + 1}  "
        handler.name = system_name.strip()
        # plug it in
        foo = TestHandlerView(self.tabControl, handler) 
        # todo why this assignment?
        handler.parent = foo
        # add it to the tab control then rename
        self.tabControl.add(foo, sticky='nsew') 
        self.tabControl.tab(foo, text=system_name)
        logger.info(f"Added {handler.name} to main window")

    def close(self):
        for tab in self.tabControl.tabs():
            widget = self.nametowidget(tab)
            if widget.handler.isRunning.get():
                if not widget.handler.isDone.get():
                    logging.warning(f"Attempted to close while a test was running on {widget.handler.name}")
                    return
        self.winfo_toplevel().destroy()
        exit()