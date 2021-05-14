from __future__ import annotations

import tkinter as tk
from logging import Logger, getLogger
from tkinter import ttk
from typing import TYPE_CHECKING

from scalewiz.helpers.validation import can_be_pos_float

if TYPE_CHECKING:

    from scalewiz.models.test import Test


LOGGER: Logger = getLogger("scalewiz")


class TestInfo(ttk.Frame):
    """A widget for inputting Test information."""

    def __init__(self, parent: tk.Widget, test: Test) -> None:
        super().__init__(parent)
        self.test: Test = test
        self.build()

    def build(self) -> None:
        """Builds the widget."""
        for child in self.winfo_children():
            child.destroy()

        self.grid_columnconfigure(1, weight=1)

        radio_lbl = ttk.Label(self, text="   Test Type:", anchor="e")
        radio_lbl.grid(row=0, column=0, sticky="ew")

        radio_frm = ttk.Frame(self)
        radio_frm.grid_columnconfigure(0, weight=1)
        radio_frm.grid_columnconfigure(1, weight=1)
        blank_btn = ttk.Radiobutton(
            radio_frm,
            text="Blank",
            variable=self.test.is_blank,
            value=True,
            command=self.build,
        )
        blank_btn.grid(row=0, column=0, sticky="e", padx=25)
        trial_btn = ttk.Radiobutton(
            radio_frm,
            text="Trial",
            variable=self.test.is_blank,
            value=False,
            command=self.build,
        )
        trial_btn.grid(row=0, column=1, sticky="w", padx=25)
        radio_frm.grid(row=0, column=1, sticky="ew")

        test_frm = ttk.Frame(self)
        test_frm.grid_columnconfigure(1, weight=1)

        if self.test.is_blank.get():
            # test_frm row 0 -----------------------------------------------------------
            name_lbl = ttk.Label(test_frm, text="         Name:", anchor="e")
            name_lbl.grid(row=0, column=0, sticky="ew")
            name_ent = ttk.Entry(test_frm, textvariable=self.test.name)
            name_ent.grid(row=0, column=1, sticky="ew")
            # test_frm row 1 -----------------------------------------------------------
            notes_lbl = ttk.Label(test_frm, text="Notes:", anchor="e")
            notes_lbl.grid(row=1, column=0, sticky="ew")
            notes_ent = ttk.Entry(test_frm, textvariable=self.test.notes)
            notes_ent.grid(row=1, column=1, sticky="ew")
            # spacers
            ttk.Label(test_frm, text="").grid(row=2)
            ttk.Label(test_frm, text="").grid(row=3, pady=1)

        else:
            # test_frm row 0 -----------------------------------------------------------
            chem_lbl = ttk.Label(test_frm, text="Chemical:", anchor="e")
            chem_lbl.grid(row=0, column=0, sticky="e")
            chem_ent = ttk.Entry(test_frm, textvariable=self.test.chemical)
            chem_ent.grid(row=0, column=1, sticky="ew")
            # test_frm row 1 -----------------------------------------------------------
            rate_lbl = ttk.Label(test_frm, text="Rate (ppm):", anchor="e")
            rate_lbl.grid(row=1, column=0, sticky="e")
            # validation command to ensure numeric inputs
            vcmd = self.register(lambda s: can_be_pos_float(s))
            rate_ent = ttk.Spinbox(
                test_frm,
                textvariable=self.test.rate,
                from_=1,
                to=999999,
                validate="key",
                validatecommand=(vcmd, "%P"),
            )
            rate_ent.grid(row=1, column=1, sticky="ew")
            # test_frm row 2 -----------------------------------------------------------
            clarity_lbl = ttk.Label(test_frm, text="Clarity:", anchor="e")
            clarity_lbl.grid(row=2, column=0, sticky="e")
            clarity_ent = ttk.Combobox(
                test_frm,
                values=["Clear", "Slightly hazy", "Hazy"],
                textvariable=self.test.clarity,
            )
            clarity_ent.current(0)  # default to 'Clear'
            clarity_ent.grid(row=2, column=1, sticky="ew")
            # test_frm row 3 -----------------------------------------------------------
            notes_lbl = ttk.Label(test_frm, text="Notes:", anchor="e")
            notes_lbl.grid(row=3, column=0, sticky="e")
            notes_ent = ttk.Entry(test_frm, textvariable=self.test.notes)
            notes_ent.grid(row=3, column=1, sticky="ew")

        test_frm.grid(row=1, column=0, columnspan=2, sticky="ew")
