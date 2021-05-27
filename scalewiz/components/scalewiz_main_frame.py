"""Main frame widget for the application. Manages a Notebook of TestHandlerViews."""

import logging
from pathlib import Path
from tkinter import ttk

from scalewiz.components.handler_view import TestHandlerView
from scalewiz.components.scalewiz_menu_bar import MenuBar
from scalewiz.models.test_handler import TestHandler

LOGGER = logging.getLogger("scalewiz")


class MainFrame(ttk.Frame):
    """Main Frame for the application."""

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent)
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)
        self.build()

    def build(self) -> None:
        """Build the UI."""
        self.winfo_toplevel().configure(menu=MenuBar(self).menubar)
        self.tab_control: ttk.Notebook = ttk.Notebook(self)
        self.tab_control.grid(sticky="nsew")
        self.add_handler()

    def add_handler(self) -> None:
        """Adds a new tab with an associated test handler."""
        system_name = f"  System {len(self.tab_control.tabs())+1}  "
        handler = TestHandler(
            name=system_name.strip(), root=self.winfo_toplevel().master
        )
        self.tab_control.add(
            TestHandlerView(self.tab_control, handler), sticky="nsew", text=system_name
        )
        LOGGER.info("Added %s to main window", handler.name)
        # if this is the first handler, open the most recent project
        if len(self.tab_control.tabs()) == 1:
            from scalewiz import CONFIG

            recent = CONFIG["recents"]["project"]
            if recent != "":
                recent = Path(recent)
                if recent.is_file():
                    handler.load_project(recent)

    def close(self) -> None:
        """Closes the program if no tests are running."""
        for tab in self.tab_control.tabs():
            widget: TestHandlerView = self.nametowidget(tab)
            if widget.handler.is_running:
                LOGGER.warning(
                    "Attempted to close while a test was running on %s",
                    widget.handler.name,
                )
                return
        self.quit()
