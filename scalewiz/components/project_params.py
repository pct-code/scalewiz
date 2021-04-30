"""Editor for Project params."""

from __future__ import annotations

import typing
from tkinter import ttk

from scalewiz.helpers.render import render
from scalewiz.helpers.validation import can_be_float, can_be_pos_float, can_be_pos_int

if typing.TYPE_CHECKING:
    from typing import List

    from scalewiz.models.project import Project


class ProjectParams(ttk.Frame):
    """A form for mutating experiment-relevant attributes of the Project."""

    def __init__(self, parent: ttk.Frame, project: Project):
        ttk.Frame.__init__(self, parent)
        # validation commands to ensure numeric inputs

        is_pos_int = self.register(lambda s: can_be_pos_int(s))
        is_float = self.register(lambda s: can_be_float(s))
        is_pos_float = self.register(lambda s: can_be_pos_float(s))
        # see https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html

        self.grid_columnconfigure(1, weight=1)
        # the int is the row to rener on
        entries: List[tuple[ttk.Label, ttk.Entry, int]] = []

        # row 0 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Bicarbonates (mg/L):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.bicarbs,
            from_=0,
            to=999999,
            validate="key",
            validatecommand=(is_float, "%P"),
        )
        entries.append((lbl, ent, 0))

        # row 1 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Bicarbonates increased:")
        ent = ttk.Frame(self)
        ent.grid_columnconfigure(0, weight=1)
        ent.grid_columnconfigure(1, weight=1)
        ttk.Radiobutton(
            ent,
            text="Yes",
            variable=project.bicarbs_increased,
            value=True,
        ).grid(row=0, column=0)
        ttk.Radiobutton(
            ent,
            text="No",
            variable=project.bicarbs_increased,
            value=False,
        ).grid(row=0, column=1)
        entries.append((lbl, ent, 1))

        # row 2 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Calcium (mg/L):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.calcium,
            from_=0,
            to=999999,
            validate="key",
            validatecommand=(is_float, "%P"),
        )
        entries.append((lbl, ent, 2))

        # row 3 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Chlorides (mg/L):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.chlorides,
            from_=0,
            to=999999,
            validate="key",
            validatecommand=(is_float, "%P"),
        )
        entries.append((lbl, ent, 3))

        # row 4 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Test temperature (°F):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.temperature,
            from_=0,
            to=9999,
            validate="key",
            validatecommand=(is_pos_float, "%P"),
        )
        entries.append((lbl, ent, 4))

        # row 5 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Baseline pressure (PSI):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.baseline,
            from_=0,
            to=9999,
            validate="key",
            validatecommand=(is_pos_int, "%P"),
        )
        entries.append((lbl, ent, 5))

        # row 6 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Limiting pressure (PSI):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.limit_psi,
            from_=0,
            to=9999,
            validate="key",
            validatecommand=(is_pos_int, "%P"),
        )
        entries.append((lbl, ent, 6))

        # row 7 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Time limit (min.):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.limit_minutes,
            from_=0,
            to=9999,
            validate="key",
            validatecommand=(is_pos_float, "%P"),
        )
        entries.append((lbl, ent, 7))

        # row 8 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Reading interval (s):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.interval_seconds,
            from_=1,
            to=9999,
            validate="key",
            validatecommand=(is_pos_float, "%P"),
        )
        entries.append((lbl, ent, 8))

        # row 9 --------------------------------------------------------------
        lbl = ttk.Label(self, text="Flowrate (mL/min):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.flowrate,
            from_=1,
            to=10,
            validate="key",
            validatecommand=(is_pos_float, "%P"),
        )
        entries.append((lbl, ent, 9))

        # row 10 --------------------------------------------------------------
        lbl = ttk.Label(self, text="Uptake time (s):")
        ent = ttk.Spinbox(
            self,
            textvariable=project.uptake_seconds,
            from_=0,
            to=9999,
            validate="key",
            validatecommand=(is_float, "%P"),
        )
        entries.append((lbl, ent, 10))

        for entry in entries:
            render(*entry)
