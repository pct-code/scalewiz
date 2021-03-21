"""Editor for Project metadata."""

from __future__ import annotations

import tkinter as tk
import typing
from tkinter import ttk

import tkcalendar as tkcal
from pct_scalewiz.helpers.render import render

if typing.TYPE_CHECKING:
    from pct_scalewiz.models.project import Project


class ProjectInfo(ttk.Frame):
    """Editor for Project metadata."""

    def __init__(self, parent: tk.Frame, project: Project):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Customer:")
        ent = ttk.Entry(self, textvariable=project.customer)
        lbl.grid(row=0, column=0, sticky="e")
        render(lbl, ent, 0)

        # row 1 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Submitted by:")
        ent = ttk.Entry(self, textvariable=project.submitted_by)
        render(lbl, ent, 1)

        # row 2 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Production company:")
        ent = ttk.Entry(self, textvariable=project.client)
        render(lbl, ent, 2)

        # row 3 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Field:")
        ent = ttk.Entry(self, textvariable=project.field)
        render(lbl, ent, 3)

        # row 4 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Sample point:")
        ent = ttk.Entry(self, textvariable=project.sample)
        render(lbl, ent, 4)

        # row 5 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Project name:")
        ent = ttk.Entry(self, textvariable=project.name)
        render(lbl, ent, 5)

        # row 6 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date sampled:")
        # this is to refresh the entry later
        current_value = project.sample_date.get()
        ent = tkcal.DateEntry(
            self, textvariable=project.sample_date, date_pattern="mm/dd/yyyy"
        )
        lbl.bind("<Button-1>", lambda _: project.sample_date.set(""))
        project.sample_date.set(current_value)
        render(lbl, ent, 6)

        # row 7 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date received:")
        current_value = project.received_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=project.received_date,
            date_pattern="mm/dd/yyyy",
        )
        lbl.bind("<Button-1>", lambda _: project.received_date.set(""))
        project.received_date.set(current_value)
        render(lbl, ent, 7)

        # row 8 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date completed:")
        current_value = project.completed_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=project.completed_date,
            date_pattern="mm/dd/yyyy",
        )
        lbl.bind("<Button-1>", lambda _: project.completed_date.set(""))
        project.completed_date.set(current_value)
        render(lbl, ent, 8)

        # row 9 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Analyst:")
        ent = ttk.Entry(self, textvariable=project.analyst)
        render(lbl, ent, 9)

        # row 10 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Analysis number(s):")
        ent = ttk.Entry(self, textvariable=project.numbers)
        render(lbl, ent, 10)

        # row 11 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Notes:")
        ent = ttk.Entry(self, textvariable=project.notes)
        render(lbl, ent, 11)

        # not implemented
        # row 12 ---------------------------------------------------------------
        # pathLbl = ttk.Label(self, text="File path:")
        # pathEnt = ttk.Entry(self, textvariable=parent.editor_project.path)
        # parent.render(pathLbl, pathEnt, 12)
