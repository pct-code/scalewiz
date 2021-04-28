"""Form for mutating Project objects."""

from __future__ import annotations

import os.path
import tkinter as tk
import typing
from tkinter import filedialog, ttk

from scalewiz.components.project_info import ProjectInfo
from scalewiz.components.project_params import ProjectParams
from scalewiz.components.project_report import ProjectReport
from scalewiz.helpers.configuration import open_config
from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.project import Project

if typing.TYPE_CHECKING:
    from scalewiz.models.test_handler import TestHandler


class ProjectWindow(tk.Toplevel):
    """Form for mutating Project objects.

    Has a tab control widget for separating the sub-forms.
    """

    def __init__(self, handler: TestHandler) -> None:
        tk.Toplevel.__init__(self)
        self.handler = handler
        self.editor_project = Project()
        if os.path.isfile(handler.project.path.get()):
            self.editor_project.load_json(handler.project.path.get())
        self.build()

    def build(self, reload: bool = False) -> None:
        """Destroys all child widgets, then builds the UI."""
        if reload:
            # cleanup for the GC
            for test in self.editor_project.tests:
                test.remove_traces()
            self.editor_project.remove_traces()  # clean up the old one for GC
            self.editor_project = Project()
            self.editor_project.load_json(self.handler.project.path.get())

        self.winfo_toplevel().title(f"{self.handler.name}")
        set_icon(self)
        for child in self.winfo_children():
            child.destroy()

        self.winfo_toplevel().resizable(0, 0)
        self.grid_columnconfigure(0, weight=1)
        tab_control = ttk.Notebook(self)
        tab_control.grid(row=0, column=0)
        tab_control.add(ProjectInfo(self, self.editor_project), text="Project info")
        tab_control.add(
            ProjectParams(self, self.editor_project), text="Experiment parameters"
        )
        tab_control.add(
            ProjectReport(self, self.editor_project), text="Report settings"
        )

        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Save", width=7, command=self.save).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(button_frame, text="Save as", width=7, command=self.save_as).grid(
            row=0, column=1, padx=10
        )
        ttk.Button(button_frame, text="New", width=7, command=self.new).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(
            button_frame, text="Edit defaults", width=10, command=self.edit
        ).grid(row=0, column=3, padx=5)
        button_frame.grid(row=1, column=0)

    def new(self) -> None:
        """Resets the form by connecting to a new Project."""
        self.editor_project = Project()
        self.build()

    def save(self) -> None:
        """Save the current Project to file as JSON."""
        if self.editor_project.path.get() == "":
            self.save_as()
        else:
            self.editor_project.dump_json()
            self.handler.load_project(self.editor_project.path.get())
            self.handler.view.build()

    def save_as(self) -> None:
        """Saves the Project to JSON using a Save As dialog."""
        file_path = filedialog.asksaveasfilename(
            title="Save Project As:",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{self.editor_project.name.get()}.json",
        )

        if file_path != "":
            # make sure it is JSON extension
            ext = file_path[-5:]
            if not ext in (".json", ".JSON"):
                file_path = f"{file_path}.json"
            self.editor_project.path.set(file_path)
            self.save()

    def edit(self) -> None:
        """Open the program config file."""
        open_config()
