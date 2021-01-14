"""MenuBar for the MainWindow."""

# util
import os
import tkinter as tk
from tkinter import messagebox

# internal
from .ProjectEditor import ProjectEditor

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
        
        parent.winfo_toplevel().config(menu=menubar)

    def requestProjectEdit(self):
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        if (widget.handler.isRunning.get()):
            messagebox.showwarning("Experiment Running", "Can't modify a Project while an experiment is running")
        else:
            widget.handler.modProj()

    def requestEvalutaionWindow(self):
        currentTab = self.parent.tabControl.select()
        widget = self.parent.nametowidget(currentTab)
        if widget.handler.isRunning.get():
            messagebox.showwarning("Experiment Running", "Can't modify a Project while an experiment is running")
        elif not os.path.isfile(widget.handler.project.path.get()):
            messagebox.showwarning("No Project File", "The requested Project file has not yet been saved, or is missing")
        else:
            widget.handler.evalProj()

    def showLogWindow(self):
        self.parent.parent.log_window.deiconify() # woof