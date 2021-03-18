"""Main Window Tkinter widget for the application"""

# util
import logging
from tkinter import ttk

from pct_scalewiz.components.menu_bar import MenuBar
from pct_scalewiz.components.test_handler_view import TestHandlerView
from pct_scalewiz.models.test_handler import TestHandler

logger = logging.getLogger("scalewiz")


class MainFrame(ttk.Frame):
    """Main Frame for the application."""

    def __init__(self, parent):
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
        logger.info("Added %s to main window", handler.name)

    def close(self) -> None:
        """Closes the program if no tests are running."""
        for tab in self.tab_control.tabs():
            widget = self.nametowidget(tab)
            if widget.handler.is_running.get():
                if not widget.handler.is_done.get():
                    logger.warning(
                        "Attempted to close while a test was running on %s",
                        widget.handler.name,
                    )
                    return
        self.quit()
