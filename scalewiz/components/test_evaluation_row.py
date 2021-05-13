"""Component for displaying a Test in a gridlike fashion."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

    from scalewiz.models.project import Project
    from scalewiz.models.test import Test


class TestResultRow(ttk.Frame):
    """Component for displaying a Test in a gridlike fashion."""

    def __init__(
        self, parent: tk.Frame, test: Test, project: Project, row: int
    ) -> None:
        ttk.Frame.__init__(self, parent)
        self.test = test
        # the immediate parent will be a frame "tests_frame" in the EvaluationFrame
        # self.parent.master refers to the EvaluationFrame itself
        self.parent = parent
        self.project = project
        self.row = row
        self.build()

    def build(self) -> None:
        """Make the UI."""
        cols: List[tk.Widget] = []
        # col 0 - name
        cols.append(ttk.Label(self.parent, textvariable=self.test.name))
        # col 1 - label
        cols.append(
            ttk.Entry(
                self.parent,
                textvariable=self.test.label,
                width=25,
                validate="focusout",
                validatecommand=self.update_score,
            )
        )
        # col 2 - duration
        duration = round(
            len(self.test.readings) * self.project.interval_seconds.get() / 60, 2
        )
        cols.append(
            ttk.Label(
                self.parent,
                text=f"{duration:.2f}, ({len(self.test.readings)})",
                anchor="center",
            )
        )
        # col 3 - pump to score
        to_score = ttk.Combobox(
            self.parent,
            textvariable=self.test.pump_to_score,
            values=["pump 1", "pump 2", "average"],
            state="readonly",
            width=7,
            validate="all",
            validatecommand=self.update_score,
        )
        to_score.bind("<MouseWheel>", self.update_score)
        cols.append(to_score)
        # col 4 - obs baseline
        cols.append(
            ttk.Label(
                self.parent, textvariable=self.test.observed_baseline, anchor="center"
            )
        )
        # col 5 - max psi
        cols.append(
            ttk.Label(self.parent, textvariable=self.test.max_psi, anchor="center")
        )
        # col 6 - clarity
        cols.append(
            ttk.Label(self.parent, textvariable=self.test.clarity, anchor="center")
        )
        # col 7 - notes
        cols.append(ttk.Entry(self.parent, textvariable=self.test.notes))
        # col 8 - result
        cols.append(
            ttk.Label(self.parent, textvariable=self.test.result, anchor="center")
        )
        # col 9 - include on report
        cols.append(
            ttk.Checkbutton(
                self.parent,
                variable=self.test.include_on_report,
                command=self.update_score,
            )
        )
        # col 10 - delete
        cols.append(
            ttk.Button(
                self.parent,
                command=self.remove_from_project,
                text="Delete",
                width=7,
            )
        )

        for i, col in enumerate(cols):
            if i == 0:  # left align the name col
                col.grid(row=self.row, column=i, padx=1, pady=1, sticky="w")
            if i == 7:  # make the notes col stretch
                self.parent.grid_columnconfigure(7, weight=1)
                col.grid(row=self.row, column=i, padx=1, pady=1, sticky="ew")
            else:  # defaults for the rest
                col.grid(
                    row=self.row,
                    column=i,
                    padx=1,
                    pady=1,
                )

    def remove_from_project(self) -> None:
        """Removes a Test from the parent Project, then tries to rebuild the UI."""
        msg = (
            "You are about to delete {} from {}.\n"
            "This will become permanent once you save the project.\n"
            "Do you wish to continue?"
        ).format(self.test.name.get(), self.project.name.get())
        remove = messagebox.askyesno("Delete test", msg)
        if remove and self.test in self.project.tests:
            self.project.tests.remove(self.test)
            self.parent.master.build()

    def update_score(self, *args) -> True:
        """Method to call score from a validation callback. Doesn't check anything."""
        # prevents a race condition when setting the score
        self.after(1, self.parent.master.score)
        return True
