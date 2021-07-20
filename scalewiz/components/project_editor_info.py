"""Editor for Project metadata."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

import tkcalendar as tkcal

if TYPE_CHECKING:
    from scalewiz.components.project_editor import ProjectWindow
    from scalewiz.models.project import Project


def render(lbl: ttk.Label, ent: ttk.Entry, row: int) -> None:
    """Grids a label and entry on the passed row."""
    lbl.grid(row=row, column=0, sticky="e", pady=1)
    ent.grid(row=row, column=1, sticky="ew", pady=1)


class ProjectInfo(ttk.Frame):
    """Editor for Project metadata."""

    def __init__(self, parent: ProjectWindow, project: Project) -> None:
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Customer:")
        ent = ttk.Entry(self, textvariable=project.customer)
        lbl.grid(row=0, column=0, sticky="e")
        render(lbl, ent, 0)

        # row 1 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Submitted by:")
        ent = ttk.Entry(self, textvariable=project.submitted_by)
        render(lbl, ent, 1)

        # row 2 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Production company:")
        ent = ttk.Entry(self, textvariable=project.client)
        render(lbl, ent, 2)

        # row 3 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Field:")
        ent = ttk.Entry(self, textvariable=project.field)
        render(lbl, ent, 3)

        # row 4 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Sample point:")
        ent = ttk.Entry(self, textvariable=project.sample)
        render(lbl, ent, 4)

        # row 5 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Project name:")
        ent = ttk.Entry(self, textvariable=project.name)
        render(lbl, ent, 5)

        # row 6 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Date sampled:")
        lbl.bind("<Button-1>", lambda _: project.sample_date.set(""))
        # this is to refresh the entry later (it inits with today's date)
        current_value = project.sample_date.get()
        ent = tkcal.DateEntry(
            self, textvariable=project.sample_date, date_pattern="mm/dd/yyyy"
        )
        lbl.bind("<Button-1>", lambda _: project.sample_date.set(""))
        project.sample_date.set(current_value)
        render(lbl, ent, 6)

        # row 7 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Date received:")
        lbl.bind("<Button-1>", lambda _: project.received_date.set(""))
        current_value = project.received_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=project.received_date,
            date_pattern="mm/dd/yyyy",
        )
        project.received_date.set(current_value)
        render(lbl, ent, 7)

        # row 8 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Date completed:")
        lbl.bind("<Button-1>", lambda _: project.completed_date.set(""))
        current_value = project.completed_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=project.completed_date,
            date_pattern="mm/dd/yyyy",
        )
        project.completed_date.set(current_value)
        render(lbl, ent, 8)

        # row 9 -----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Analyst:")
        ent = ttk.Entry(self, textvariable=project.analyst)
        render(lbl, ent, 9)

        # row 10 ----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Analysis number(s):")
        ent = ttk.Entry(self, textvariable=project.numbers)
        render(lbl, ent, 10)

        # row 11 ----------------------------------------------------------------------
        lbl = ttk.Label(self, text="Notes:")
        ent = ttk.Entry(self, textvariable=project.notes)
        render(lbl, ent, 11)

        # row 12 ----------------------------------------------------------------------
        pathLbl = ttk.Label(self, text="File path:")
        xscrollbar = ttk.Scrollbar(self, orient="horizontal")
        pathText = tk.Text(
            self, wrap="none", xscrollcommand=xscrollbar.set, height=1, width=20
        )
        xscrollbar.configure(command=pathText.xview)
        pathText.insert("end", parent.editor_project.path.get())
        pathText.see("end")
        pathLbl.grid(row=12, column=0, sticky="e", pady=1)
        pathText.grid(row=12, column=1, sticky="ew", pady=1)
        xscrollbar.grid(row=13, column=1, sticky="nsew")
