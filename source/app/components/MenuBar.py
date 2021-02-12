"""MenuBar for the MainWindow."""

# util
import logging
import os
import tkinter as tk
from tkinter import messagebox, ttk

from .EvaluationFrame import EvaluationFrame
from .RinseModal import RinseModal
# internal
from .ProjectEditor import ProjectEditor

logger = logging.getLogger('scalewiz')

class MenuBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # expecting parent to be the toplevel parent of the main frame
        self.parent = parent

        menubar = tk.Menu()
        menubar.add_command(label="Add System", command=lambda: parent.addTestHandler())
        menubar.add_command(label="Project", command=lambda: self.requestProjectEdit())
        menubar.add_command(label="Evaluation", command=lambda: self.requestEvalutaionWindow())
        menubar.add_command(label="Log", command=lambda: self.showLogWindow())
        menubar.add_command(label="Rinse", command=lambda: self.showRinse())
        
        parent.winfo_toplevel().config(menu=menubar)

    def requestProjectEdit(self):
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        # if (widget.handler.isRunning.get()):
        #     messagebox.showwarning("Experiment Running", "Can't modify a Project while an experiment is running")
        # else:
        self.modProj(widget.handler)

    def requestEvalutaionWindow(self):
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        # if widget.handler.isRunning.get():
        #     messagebox.showwarning("Experiment Running", "Can't modify a Project while an experiment is running")
        if not os.path.isfile(widget.handler.project.path.get()):
            messagebox.showwarning("No Project File", "The requested Project file has not yet been saved, or is missing")
        else:
            self.evalProj(widget.handler)

    def showLogWindow(self):
        # todo this is not elegant
        self.parent.parent.log_window.deiconify() # woof

    def showRinse(self):
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)

        window = tk.Toplevel()
        rinse = RinseModal(widget.handler, window)
        rinse.grid()
        window.resizable(0, 0)

       


# todo move close editors method off of testhandler

    def modProj(self, handler):
        if len(handler.editors) > 0: 
            messagebox.showwarning("Project is locked", "Can't modify a Project while it is being accessed")
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", lambda: handler.closeEditors())
        window.resizable(0, 0)
        handler.editors.append(window)
        editor = ProjectEditor(window, handler)
        editor.grid()
        logger.info(f"{handler.name}: Opened an editor window for {handler.project.name.get()}")

    def evalProj(self, handler):
        if len(handler.editors) > 0: 
            messagebox.showwarning("Project is locked", "Can't modify a Project while it is being accessed")
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", lambda: handler.closeEditors())
        window.resizable(0, 0)
        handler.editors.append(window)
        editor = EvaluationFrame(window, handler)
        editor.grid()
        logger.info(f"{handler.name}: Opened an evaluation window for {handler.project.name.get()}")
