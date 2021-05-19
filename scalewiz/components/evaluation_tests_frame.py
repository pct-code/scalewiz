from __future__ import annotations

import tkinter as tk
from logging import Logger, getLogger
from tkinter import ttk
from typing import TYPE_CHECKING

from scalewiz.components.test_evaluation_row import TestResultRow
from scalewiz.models.project import Project

if TYPE_CHECKING:
    from tkinter.font import Font
    from typing import List

    from scalewiz.models.test import Test


LOGGER: Logger = getLogger("scalewiz")


class EvaluationTestsFrame(ttk.Frame):
    """A widget for selecting devices."""

    def __init__(
        self,
        parent: ttk.Frame,
        project: Project,
        mode: str,
        font: Font,
        col_labels: bool = True,
    ) -> None:
        super().__init__(parent)
        self.tests: List[Test] = []
        self.mode: str = mode
        if self.mode == "blanks":
            self.label: str = "Blanks:"
        elif self.mode == "trials":
            self.label: str = "Trials:"
        self.font: Font = font
        self.project: Project = project
        self.col_labels: bool = col_labels
        # child TestResultRow widgets come to find these
        self.baseline_len: int = None
        self.name_len: int = None
        self.clarity_len: int = None
        self.max_psi_len: int = None
        self.minutes_len: int = None

        self.build()

    def build(self) -> None:
        """Build the UI."""
        for child in self.winfo_children():
            child.destroy()
        self.grid_columnconfigure(0, weight=1)

        self.sort_tests()
        self.set_label_lengths()

        if self.col_labels:
            col_header = ttk.Frame(self)
            labels = []
            labels.append(
                tk.Label(
                    col_header,
                    text="Name",
                    font=self.font,
                    width=self.name_len - 5,
                    anchor="w",
                )
            )
            labels.append(
                tk.Label(col_header, text="Label", font=self.font, width=21, anchor="w")
            )
            labels.append(
                tk.Label(
                    col_header,
                    text="Minutes",
                    font=self.font,
                    width=self.minutes_len + 10,
                    anchor="w",
                )
            )
            labels.append(tk.Label(col_header, text="Pump", font=self.font, anchor="w"))
            labels.append(
                tk.Label(col_header, text="Baseline", font=self.font, anchor="w")
            )
            labels.append(tk.Label(col_header, text="Max", font=self.font, anchor="w"))
            labels.append(
                tk.Label(col_header, text="Clarity", font=self.font, anchor="w")
            )
            labels.append(
                tk.Label(col_header, text="Notes", font=self.font, anchor="w")
            )
            labels.append(
                tk.Label(col_header, text="Result", font=self.font, anchor="w")
            )
            labels.append(
                tk.Label(col_header, text="Report", font=self.font, anchor="w")
            )
            labels.append(tk.Label(col_header, text=" ", font=self.font, anchor="w"))

            for i, lbl in enumerate(labels):
                col_header.grid_columnconfigure(i, weight=1)
                lbl.grid(row=0, column=i, padx=0, sticky="w")
            col_header.grid(row=0, column=0, sticky="ew")

        type_header = ttk.Label(self, text=self.label, font=self.font)
        type_header.grid(row=1, column=0, sticky="ew", padx=0, pady=1)

        for i, test in enumerate(self.tests):
            row = TestResultRow(self, test, self.project)
            row.grid(row=i + 2, column=0, sticky="ew")

    def sort_tests(self) -> None:
        """
        Sort through the editor_project, populating the lists of blanks and trials.
        """
        self.tests.clear()
        for test in self.project.tests:
            if self.mode == "blanks" and test.is_blank.get():
                self.tests.append(test)
            elif self.mode == "trials" and not test.is_blank.get():
                self.tests.append(test)

    def set_label_lengths(self) -> None:
        """Sets label length values."""
        name_len = int()
        baseline_len = int()
        clarity_len = int()

        for test in self.project.tests:
            _name_len = len(test.name.get())
            if _name_len > name_len:
                name_len = _name_len

            _baseline_len = len(str(test.observed_baseline.get()))
            if _baseline_len > baseline_len:
                baseline_len = _baseline_len

            _clarity_len = len(test.clarity.get())
            if _clarity_len > clarity_len:
                clarity_len = _clarity_len

        minutes_len = len(str(self.project.limit_minutes.get()))
        max_psi_len = len(str(self.project.limit_psi.get()))

        self.name_len = name_len
        self.clarity_len = clarity_len
        self.baseline_len = baseline_len
        self.minutes_len = minutes_len
        self.max_psi_len = max_psi_len
