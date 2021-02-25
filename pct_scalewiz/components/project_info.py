"""Editor for Project metadata."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

import tkcalendar as tkcal

# todo #2 implement some form of entry validation targeting disallowed chars for a filepath


class ProjectInfo(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 ---------------------------------------------------------------
        custLbl = ttk.Label(self, text="Customer:")
        custEnt = ttk.Entry(self, textvariable=parent.editorProject.customer)
        parent.render(custLbl, custEnt, 0)

        # row 1 ---------------------------------------------------------------
        subLbl = ttk.Label(self, text="Submitted by:")
        subEnt = ttk.Entry(self, textvariable=parent.editorProject.submittedBy)
        parent.render(subLbl, subEnt, 1)

        # row 2 ---------------------------------------------------------------
        prodLbl = ttk.Label(self, text="Production company:")
        prodEnt = ttk.Entry(self, textvariable=parent.editorProject.productionCo)
        parent.render(prodLbl, prodEnt, 2)

        # row 3 ---------------------------------------------------------------
        fieldLbl = ttk.Label(self, text="Field:")
        fieldEnt = ttk.Entry(self, textvariable=parent.editorProject.field)
        parent.render(fieldLbl, fieldEnt, 3)

        # row 4 ---------------------------------------------------------------
        sampleLbl = ttk.Label(self, text="Sample point:")
        sampleEnt = ttk.Entry(self, textvariable=parent.editorProject.sample)
        parent.render(sampleLbl, sampleEnt, 4)

        # row 5 ---------------------------------------------------------------
        projLbl = ttk.Label(self, text="Project name:")
        projEnt = ttk.Entry(self, textvariable=parent.editorProject.name)
        parent.render(projLbl, projEnt, 5)

        # row 6 ---------------------------------------------------------------
        sampleDateLbl = ttk.Label(self, text="Date sampled:")
        d = parent.editorProject.sampleDate.get()
        sampleDateEnt = tkcal.DateEntry(
            self, textvariable=parent.editorProject.sampleDate, date_pattern="mm/dd/Y"
        )
        sampleDateLbl.bind(
            "<Button-1>", lambda _: parent.editorProject.sampleDate.set("")
        )
        parent.editorProject.sampleDate.set(d)
        parent.render(sampleDateLbl, sampleDateEnt, 6)

        # row 7 ---------------------------------------------------------------
        recDateLbl = ttk.Label(self, text="Date received:")
        d = parent.editorProject.recDate.get()
        recDateEnt = tkcal.DateEntry(
            self, textvariable=parent.editorProject.recDate, date_pattern="mm/dd/yyyy"
        )
        recDateLbl.bind("<Button-1>", lambda _: parent.editorProject.recDate.set(""))
        parent.editorProject.recDate.set(d)
        parent.render(recDateLbl, recDateEnt, 7)

        # row 8 ---------------------------------------------------------------
        compDateLbl = ttk.Label(self, text="Date completed:")
        d = parent.editorProject.compDate.get()
        compDateEnt = tkcal.DateEntry(
            self, textvariable=parent.editorProject.compDate, date_pattern="mm/dd/yyyy"
        )
        compDateLbl.bind("<Button-1>", lambda _: parent.editorProject.compDate.set(""))
        parent.editorProject.compDate.set(d)
        parent.render(compDateLbl, compDateEnt, 8)

        # row 9 ---------------------------------------------------------------
        analystLbl = ttk.Label(self, text="Analyst:")
        analystEnt = ttk.Entry(self, textvariable=parent.editorProject.analyst)
        parent.render(analystLbl, analystEnt, 9)

        # row 10 ---------------------------------------------------------------
        analNoLbl = ttk.Label(self, text="Analysis number(s):")
        analNoEnt = ttk.Entry(self, textvariable=parent.editorProject.numbers)
        parent.render(analNoLbl, analNoEnt, 10)

        # row 11 ---------------------------------------------------------------
        notesLbl = ttk.Label(self, text="Notes:")
        notesEnt = ttk.Entry(self, textvariable=parent.editorProject.notes)
        parent.render(notesLbl, notesEnt, 11)

        # not implemented
        # row 12 ---------------------------------------------------------------
        # pathLbl = ttk.Label(self, text="File path:")
        # pathEnt = ttk.Entry(self, textvariable=parent.editorProject.path)
        # parent.render(pathLbl, pathEnt, 12)
