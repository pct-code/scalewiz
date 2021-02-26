"""Main Window Tkinter widget for the application"""

# util
import logging
import sys
import tkinter as tk
from tkinter import ttk

from pct_scalewiz.components.base_frame import BaseFrame
from pct_scalewiz.components.menu_bar import MenuBar
from pct_scalewiz.components.test_handler_view import TestHandlerView
from pct_scalewiz.models.test_handler import TestHandler

logger = logging.getLogger("scalewiz")


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
        self.tabControl.grid(sticky="nsew")
        self.addTestHandler()

    def addTestHandler(self):
        # make a new handler 🤠
        system_name = f"  System {len(self.tabControl.tabs()) + 1}  "
        name = (
            system_name.strip()
        )  # todo perhaps we could pass this as arg to TestHandler init
        handler = TestHandler(name)
        # plug it in 🔌
        view = TestHandlerView(self.tabControl, handler)
        # todo why this assignment? the handler's 'parent' isn't a view. this can't be right, there must be a better way
        handler.parent = view  # 😬
        # add it to the tab control then rename
        self.tabControl.add(view, sticky="nsew")
        self.tabControl.tab(view, text=system_name)
        logger.info("Added %s to main window", handler.name)

    def close(self):
        for tab in self.tabControl.tabs():
            widget = self.nametowidget(tab)
            if widget.handler.is_running.get():
                if not widget.handler.isDone.get():
                    logger.warning(
                        "Attempted to close while a test was running on %s",
                        widget.handler.name,
                    )
                    return
        sys.exit()
