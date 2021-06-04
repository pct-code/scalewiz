"""MenuBar for the MainWindow."""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path

# from time import time
from tkinter.messagebox import showinfo
from typing import TYPE_CHECKING

from scalewiz.components.evaluation_window import EvaluationWindow
from scalewiz.components.project_editor import ProjectWindow
from scalewiz.components.scalewiz_rinse_window import RinseWindow
from scalewiz.helpers.show_help import show_help

LOGGER = logging.getLogger("scalewiz")

if TYPE_CHECKING:
    from scalewiz.components.handler_view import TestHandlerView
    from scalewiz.components.scalewiz_main_frame import MainFrame


class MenuBar:
    """Menu bar to be displayed on the Main Frame."""

    def __init__(self, parent: MainFrame) -> None:
        # expecting parent to be the toplevel parent of the main frame
        self.parent = parent

        menubar = tk.Menu()
        menubar.add_command(label="Add System", command=self.parent.add_handler)
        # make project cascade
        project_menu = tk.Menu(tearoff=0)
        project_menu.add_command(label="New/Edit", command=self.spawn_editor)
        project_menu.add_command(
            label="Load existing", command=self.request_project_load
        )
        menubar.add_cascade(label="Project", menu=project_menu)
        # resume making buttons
        menubar.add_command(label="Evaluation", command=self.spawn_evaluator)
        menubar.add_command(label="Rinse", command=self.spawn_rinse)
        menubar.add_command(
            label="Log", command=self.parent.master.log_window.deiconify
        )
        menubar.add_command(label="Help", command=show_help)
        menubar.add_command(label="About", command=self.about)

        # menubar.add_command(label="Debug", command=self._debug)
        self.menubar = menubar

    def spawn_editor(self) -> None:
        """Spawn a Toplevel for editing Projects."""
        current_tab = self.parent.tab_control.select()
        widget = self.parent.nametowidget(current_tab)
        window = ProjectWindow(widget.handler)
        widget.handler.views.append(window)
        LOGGER.debug("Spawned a Project Editor window for %s", widget.handler.name)

    def spawn_evaluator(self) -> None:
        """Requests to open an evalutaion window for the currently selected Project."""
        current_tab = self.parent.tab_control.select()
        widget: TestHandlerView = self.parent.nametowidget(current_tab)
        window = EvaluationWindow(widget.handler)
        widget.handler.views.append(window)
        LOGGER.debug("Spawned an Evaluation window for %s", widget.handler.name)

    def request_project_load(self) -> None:
        """Request that the currently selected TestHandler load a Project."""
        # build a list of currently loaded projects, and pass to the handler
        currently_loaded = set()
        for tab in self.parent.tab_control.tabs():
            widget = self.parent.nametowidget(tab)
            currently_loaded.add(Path(widget.handler.project.path.get()))
        # the handler will check to make sure we don't load a project in duplicate
        current_tab = self.parent.tab_control.select()
        widget = self.parent.nametowidget(current_tab)
        widget.handler.load_project(loaded=currently_loaded)
        widget.build()

    def spawn_rinse(self) -> None:
        """Shows a RinseFrame in a new Toplevel."""
        current_tab = self.parent.tab_control.select()
        widget = self.parent.nametowidget(current_tab)
        RinseWindow(widget.handler)
        LOGGER.debug("Spawned a Rinse window for %s", widget.handler.name)

    def about(self) -> None:
        showinfo(
            "About",
            (
                "Copyright  (C) 2021  Alex Whittington\n\n"
                "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.\n\n"  # noqa: E501
                "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\n"  # noqa: E501
                "You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>."  # noqa: E501
            ),
        )

    def _debug(self) -> None:
        """Used for debugging."""
        pass
        # LOGGER.warn("DEBUGGING")

        # current_tab = self.parent.tab_control.select()
        # widget: TestHandlerView = self.parent.nametowidget(current_tab)
        # widget.handler.setup_pumps()
        # t0 = time()
        # widget.handler.pump1.pressure
        # widget.handler.pump2.pressure
        # t1 = time()
        # widget.handler.close_pumps()
        # LOGGER.warn("collected 2 pressures in %s", t1 - t0)
        # widget.handler.rebuild_views()
        # widget.bell()
