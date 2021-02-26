"""Form for mutating Project objects."""

# util
import os.path
import tkinter as tk
from tkinter import filedialog, ttk

# internal
from pct_scalewiz.models.project import Project
from pct_scalewiz.components.base_frame import BaseFrame
from pct_scalewiz.components.project_info import ProjectInfo
from pct_scalewiz.components.project_params import ProjectParams
from pct_scalewiz.components.project_report import ProjectReport


class ProjectEditor(BaseFrame):
    def __init__(self, parent, handler):
        BaseFrame.__init__(self, parent)
        self.handler = handler
        self.grid_columnconfigure(0, weight=1)
        if os.path.isfile(handler.project.path.get()):
            self.editorProject = Project.loadJson(handler.project.path.get())
            self.editorProject.path.set(handler.project.path.get())
        else:
            self.editorProject = Project()
        self.build()

    def build(self):
        tabControl = ttk.Notebook(self)
        tabControl.grid(row=0, column=0)

        tabControl.add(ProjectInfo(self), text="Project info")
        tabControl.add(ProjectParams(self), text="Experiment parameters")
        tabControl.add(ProjectReport(self), text="Report settings")

        btnFrm = ttk.Frame(self)
        ttk.Button(btnFrm, text="Save", width=7, command=lambda: self.save()).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btnFrm, text="Save as", width=7, command=lambda: self.saveAs()).grid(
            row=0, column=1, padx=10
        )
        ttk.Button(btnFrm, text="New", width=7, command=lambda: self.new()).grid(
            row=0, column=2, padx=5
        )
        btnFrm.grid(row=1, column=0)

    def render(self, label, entry, row):
        """Render the passed label and entry on the passed row."""
        label.grid(row=row, column=0, sticky=tk.E)
        entry.grid(row=row, column=1, sticky=tk.E + tk.W, pady=1)

    def new(self):
        self.editorProject = Project()
        self.build()

    def save(self):
        if self.editorProject.path.get() == "":
            self.saveAs()
        else:
            Project.dumpJson(self.editorProject, self.editorProject.path.get())
            self.handler.project = Project.loadJson(self.editorProject.path.get())
            # todo how about a call to build instead?
            self.handler.parent.build()

    def saveAs(self):
        file = filedialog.asksaveasfilename(
            title="Save Project As:",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{self.editorProject.name.get()}.json",
        )

        if not file == "":
            # make sure it is JSON extension
            ext = file[-5:]
            if not ext in (".json", ".JSON"):
                file = f"{file}.json"
            self.editorProject.path.set(file)
            self.save()
