"""MenuBar for the MainWindow."""

from __future__ import annotations

import logging
import os
import tkinter as tk
import typing
from tkinter import messagebox

from pct_scalewiz.components.rinse_frame import RinseFrame
from pct_scalewiz.helpers.evaluate_project import evaluate_project
from pct_scalewiz.helpers.modify_project import modify_project
from pct_scalewiz.helpers.show_help import show_help

if typing.TYPE_CHECKING:
    from pct_scalewiz.components.base_frame import BaseFrame
    from pct_scalewiz.models.test_handler import TestHandler

# todo #9 port over the old chlorides / ppm calculators

logger = logging.getLogger("scalewiz")


class MenuBar:
    """Menu bar to be displayed on the Main Frame."""

    def __init__(self, parent: BaseFrame) -> None:
        # expecting parent to be the toplevel parent of the main frame
        self.main_frame = parent

        menu_bar = tk.Menu()
        menu_bar.add_command(
            label="Add System", command=lambda: self.main_frame.add_handler()
        )

        project_menu = tk.Menu(tearoff=0)
        project_menu.add_command(
            label="New/Edit", command=lambda: self.request_project_edit()
        )
        project_menu.add_command(
            label="Load existing", command=lambda: self.request_project_load()
        )

        menu_bar.add_cascade(label="Project", menu=project_menu)
        menu_bar.add_command(
            label="Evaluation", command=lambda: self.request_eval_window()
        )
        menu_bar.add_command(
            label="Log", command=lambda: self.main_frame.parent.log_window.deiconify()
        )
        menu_bar.add_command(label="Rinse", command=lambda: self.show_rinse())
        menu_bar.add_command(label="Help", command=lambda: show_help())

        self.main_frame.winfo_toplevel().config(menu=menu_bar)

    def request_project_edit(self) -> None:
        """Requests to open an editor window for the currently selected Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        modify_project(widget.handler)

    def request_eval_window(self) -> None:
        """Requests to open an evalutaion window for the currently selected Project."""
        current_tab = self.main_frame.tab_control.select()
        widget = self.main_frame.nametowidget(current_tab)
        if os.path.isfile(widget.handler.project.path.get()):
            evaluate_project(widget.handler)
        else:
            messagebox.showwarning(
                "No Project File",
                "The requested Project file has not yet been saved, or is missing",
            )

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

    # todo move close editors method off of testhandler
