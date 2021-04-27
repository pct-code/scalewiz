"""MenuBar for the MainWindow."""

from __future__ import annotations

import logging
import tkinter as tk

from scalewiz.components.evaluation_window import EvaluationWindow
from scalewiz.components.project_window import ProjectWindow
from scalewiz.components.rinse_window import RinseWindow
from scalewiz.helpers.show_help import show_help

# todo #9 port over the old chlorides / ppm calculators

LOGGER = logging.getLogger("scalewiz")


class MenuBar:
    """Menu bar to be displayed on the Main Frame."""

    def __init__(self, parent: tk.Frame) -> None:
        # expecting parent to be the toplevel parent of the main frame
        self.main_frame = parent

        menubar = tk.Menu()
        menubar.add_command(label="Add System", command=self.main_frame.add_handler)

        project_menu = tk.Menu(tearoff=0)
        project_menu.add_command(label="New/Edit", command=self.spawn_editor)
        project_menu.add_command(
            label="Load existing", command=self.request_project_load
        )

        menubar.add_cascade(label="Project", menu=project_menu)
        menubar.add_command(label="Evaluation", command=self.spawn_evaluator)
        menubar.add_command(
            label="Log", command=self.main_frame.parent.log_window.deiconify
        )
        menubar.add_command(label="Rinse", command=self.spawn_rinse)
        menubar.add_command(label="Help", command=show_help)

        # debug
        menubar.add_command(label="Debug", command=self.debug)

        self.main_frame.winfo_toplevel().configure(menu=menubar)

    def spawn_editor(self) -> None:
        """Spawn a Toplevel for editing Projects."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        window = ProjectWindow(widget.handler)
        widget.handler.editors.append(window)
        LOGGER.debug('Spawned a Project Editor window for %s', widget.handler.name)

    def spawn_evaluator(self) -> None:
        """Requests to open an evalutaion window for the currently selected Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        window = EvaluationWindow(widget.handler)
        widget.handler.editors.append(window)
        LOGGER.debug('Spawned an Evaluation window for %s', widget.handler.name)

    def request_project_load(self) -> None:
        """Request that the currently selected TestHandler load a Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        widget.handler.load_project()
        widget.build()

    def spawn_rinse(self) -> None:
        """Shows a RinseFrame in a new Toplevel."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        RinseWindow(widget.handler)
        LOGGER.debug('Spawned a Rinse window for %s', widget.handler.name)

    def debug(self) -> None:
        """used for debugging"""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        widget.handler.rebuild_editors()
        widget.bell()
