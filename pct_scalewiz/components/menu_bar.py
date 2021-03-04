"""MenuBar for the MainWindow."""

from __future__ import annotations

import logging
import os
import tkinter as tk
import typing

from pct_scalewiz.components.evaluation_window import EvaluationWindow
from pct_scalewiz.components.project_window import ProjectWindow
from pct_scalewiz.components.rinse_frame import RinseFrame
from pct_scalewiz.helpers.show_help import show_help

# todo #9 port over the old chlorides / ppm calculators

logger = logging.getLogger("scalewiz")


class MenuBar:
    """Menu bar to be displayed on the Main Frame."""

    def __init__(self, parent: tk.Frame) -> None:
        # expecting parent to be the toplevel parent of the main frame
        self.main_frame = parent

        menu_bar = tk.Menu()
        menu_bar.add_command(
            label="Add System", command=lambda: self.main_frame.add_handler()
        )

        project_menu = tk.Menu(tearoff=0)
        project_menu.add_command(label="New/Edit", command=lambda: self.spawn_editor())
        project_menu.add_command(
            label="Load existing", command=lambda: self.request_project_load()
        )

        menu_bar.add_cascade(label="Project", menu=project_menu)
        menu_bar.add_command(label="Evaluation", command=lambda: self.spawn_evaluator())
        menu_bar.add_command(
            label="Log", command=lambda: self.main_frame.parent.log_window.deiconify()
        )
        menu_bar.add_command(label="Rinse", command=lambda: self.show_rinse())
        menu_bar.add_command(label="Help", command=lambda: show_help())

        self.main_frame.winfo_toplevel().configure(menu=menu_bar)

    def spawn_editor(self) -> None:
        """Spawn a Toplevel for editing Projects."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        window = ProjectWindow(widget.handler)
        widget.handler.editors.append(window)

    def spawn_evaluator(self) -> None:
        """Requests to open an evalutaion window for the currently selected Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        window = EvaluationWindow(widget.handler)
        widget.handler.editors.append(window)

    def request_project_load(self) -> None:
        """Request that the currently selected TestHandler load a Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        widget.handler.load_project()
        widget.build()

    def show_rinse(self) -> None:
        """Shows a RinseFrame in a new Toplevel."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        window = tk.Toplevel()
        rinse = RinseFrame(widget.handler, window)
        rinse.grid()
        window.resizable(0, 0)
