"""Editor for Project metadata."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

import tkcalendar as tkcal

# todo #2 implement some form of entry validation targeting disallowed chars for a filepath

# todo give these project sub frames a regular build pattern


class ProjectInfo(ttk.Frame):
    """Editor for Project metadata."""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Customer:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.customer)
        parent.render(lbl, ent, 0)

        # row 1 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Submitted by:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.submitted_by)
        parent.render(lbl, ent, 1)

        # row 2 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Production company:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.client)
        parent.render(lbl, ent, 2)

        # row 3 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Field:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.field)
        parent.render(lbl, ent, 3)

        # row 4 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Sample point:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.sample)
        parent.render(lbl, ent, 4)

        # row 5 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Project name:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.name)
        parent.render(lbl, ent, 5)

        # row 6 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date sampled:")
        # this is to refresh the entry later
        d = parent.editorProject.sample_date.get()
        ent = tkcal.DateEntry(
            self, textvariable=parent.editorProject.sample_date, date_pattern="mm/dd/Y"
        )
        lbl.bind("<Button-1>", lambda _: parent.editorProject.sample_date.set(""))
        parent.editorProject.sample_date.set(d)
        parent.render(lbl, ent, 6)

        # row 7 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date received:")
        d = parent.editorProject.received_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=parent.editorProject.received_date,
            date_pattern="mm/dd/yyyy",
        )
        lbl.bind("<Button-1>", lambda _: parent.editorProject.received_date.set(""))
        parent.editorProject.received_date.set(d)
        parent.render(lbl, ent, 7)

        # row 8 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Date completed:")
        d = parent.editorProject.completed_date.get()
        ent = tkcal.DateEntry(
            self,
            textvariable=parent.editorProject.completed_date,
            date_pattern="mm/dd/yyyy",
        )
        lbl.bind("<Button-1>", lambda _: parent.editorProject.completed_date.set(""))
        parent.editorProject.completed_date.set(d)
        parent.render(lbl, ent, 8)

        # row 9 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Analyst:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.analyst)
        parent.render(lbl, ent, 9)

        # row 10 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Analysis number(s):")
        ent = ttk.Entry(self, textvariable=parent.editorProject.numbers)
        parent.render(lbl, ent, 10)

        # row 11 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Notes:")
        ent = ttk.Entry(self, textvariable=parent.editorProject.notes)
        parent.render(lbl, ent, 11)

        # not implemented
        # row 12 ---------------------------------------------------------------
        # pathLbl = ttk.Label(self, text="File path:")
        # pathEnt = ttk.Entry(self, textvariable=parent.editorProject.path)
        # parent.render(pathLbl, pathEnt, 12)
