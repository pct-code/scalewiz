"""MenuBar for the MainWindow."""

# util
import logging
import os
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk


# internal
from pct_scalewiz.components.evaluation_frame import EvaluationFrame
from pct_scalewiz.components.project_editor import ProjectEditor
from pct_scalewiz.components.rinse_frame import RinseFrame
from pct_scalewiz.helpers.show_help import show_help

# todo #9 port over the old chlorides / ppm calculators

logger = logging.getLogger("scalewiz")


class MenuBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # expecting parent to be the toplevel parent of the main frame
        self.parent = parent

        menubar = tk.Menu()
        menubar.add_command(label="Add System", command=lambda: parent.addTestHandler())

        projMenu = tk.Menu(tearoff=0)
        projMenu.add_command(
            label="New/Edit", command=lambda: self.request_project_edit()
        )
        projMenu.add_command(
            label="Load existing", command=lambda: self.request_project_load()
        )

        menubar.add_cascade(label="Project", menu=projMenu)
        menubar.add_command(
            label="Evaluation", command=lambda: self.request_eval_window()
        )
        menubar.add_command(
            label="Log", command=lambda: self.parent.parent.log_window.deiconify()
        )
        menubar.add_command(label="Rinse", command=lambda: self.showRinse())
        menubar.add_command(label="Help", command=lambda: show_help())

        parent.winfo_toplevel().config(menu=menubar)

    def request_project_edit(self) -> None:
        """Requests to open an editor window for the currently selected Project."""
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        self.modProj(widget.handler)

    def request_eval_window(self) -> None:
        """Requests to open an evalutaion window for the currently selected Project."""
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        if not os.path.isfile(widget.handler.project.path.get()):
            messagebox.showwarning(
                "No Project File",
                "The requested Project file has not yet been saved, or is missing",
            )
        else:
            self.evalProj(widget.handler)

    def request_project_load(self) -> None:
        """Request that the currently selected TestHandler load a Project."""
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        widget.handler.load_project()
        widget.build()

    def showRinse(self) -> None:
        """Shows a RinseFrame in a new Toplevel."""
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)

        window = tk.Toplevel()
        rinse = RinseFrame(widget.handler, window)
        rinse.grid()
        window.resizable(0, 0)

    # todo move close editors method off of testhandler

    def modProj(self, handler):
        if len(handler.editors) > 0:
            messagebox.showwarning(
                "Project is locked", "Can't modify a Project while it is being accessed"
            )
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", lambda: handler.close_editors())
        window.resizable(0, 0)
        handler.editors.append(window)
        editor = ProjectEditor(window, handler)
        editor.grid()
        logger.info(
            f"{handler.name}: Opened an editor window for {handler.project.name.get()}"
        )

    def evalProj(self, handler):
        if len(handler.editors) > 0:
            messagebox.showwarning(
                "Project is locked", "Can't modify a Project while it is being accessed"
            )
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", lambda: handler.close_editors())
        window.resizable(0, 0)
        handler.editors.append(window)
        editor = EvaluationFrame(window, handler)
        editor.grid()
        logger.info(
            f"{handler.name}: Opened an evaluation window for {handler.project.name.get()}"
        )
