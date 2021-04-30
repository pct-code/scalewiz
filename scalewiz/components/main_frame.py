"""Main frame widget for the application."""

# util
import logging
from tkinter import ttk

from scalewiz.components.menu_bar import MenuBar
from scalewiz.components.test_handler_view import TestHandlerView
from scalewiz.helpers.configuration import get_config
from scalewiz.models.test_handler import TestHandler

LOGGER = logging.getLogger("scalewiz")


class MainFrame(ttk.Frame):
    """Main Frame for the application."""

    def __init__(self, parent: ttk.Frame) -> None:
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)
        self.build()

    def build(self) -> None:
        """Build the UI."""
        MenuBar(self)  # this will apply itself to the current Toplevel
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(sticky="nsew")
        self.add_handler()

    def add_handler(self) -> None:
        """Adds a new tab with an associated test handler."""
        system_name = f"  System {len(self.tab_control.tabs()) + 1}  "
        handler = TestHandler(name=system_name.strip())
        # plug it in 🔌
        view = TestHandlerView(self.tab_control, handler)
        handler.set_view(view)  # we want to be able to rebuild it later
        self.tab_control.add(view, sticky="nsew")
        self.tab_control.tab(view, text=system_name)
        LOGGER.info("Added %s to main window", handler.name)
        # if this is the first handler, open the most recent project
        if len(self.tab_control.tabs()) == 1:
            config = get_config()
            handler.load_project(config["recents"].get("project"))

    def close(self) -> None:
        """Closes the program if no tests are running."""
        for tab in self.tab_control.tabs():
            widget = self.nametowidget(tab)
            if widget.handler.is_running.get():
                if not widget.handler.is_done.get():
                    LOGGER.warning(
                        "Attempted to close while a test was running on %s",
                        widget.handler.name,
                    )
                    return
        self.quit()
