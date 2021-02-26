"""Component for displaying a Test in a gridlike fashion."""

import tkinter as tk
from tkinter import messagebox, ttk


class TestResultRow(ttk.Frame):
    def __init__(self, parent, test, project, row):
        ttk.Frame.__init__(self, parent)
        self.test = test
        self.parent = parent
        self.project = project
        self.row = row
        self.build()

    def build(self):
        cols = []
        # col 0 - name
        cols.append(ttk.Label(self.parent, textvariable=self.test.name))
        # col 1 - report as
        cols.append(ttk.Entry(self.parent, textvariable=self.test.report_as, width=25))
        # col 2 - duration
        duration = round(len(self.test.readings) * self.project.interval.get() / 60, 2)
        cols.append(
            ttk.Label(
                self.parent,
                text=f"{duration:.2f}, ({len(self.test.readings)})",
                anchor="center",
            )
        )
        # col 3 - to consider
        cols.append(
            ttk.Combobox(
                self.parent,
                textvariable=self.test.toConsider,
                values=["pump 1", "pump 2", "average"],
                state="readonly",
                width=7,
            )
        )
        # col 4 - obs baseline
        cols.append(
            ttk.Label(self.parent, textvariable=self.test.obsBaseline, anchor="center")
        )
        # col 5 - max psi
        cols.append(
            ttk.Label(self.parent, textvariable=self.test.maxPSI, anchor="center")
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
        # col 9 - on report
        cols.append(ttk.Checkbutton(self.parent, variable=self.test.includeOnRep))
        # col 10 - delete
        cols.append(
            ttk.Button(
                self.parent,
                command=lambda: self.removeFromProject(),
                text="Delete",
                width=7,
            )
        )

        self.parent.grid_columnconfigure(7, weight=1)
        for i in range(len(cols)):
            if i == 0:
                cols[i].grid(row=self.row, column=i, padx=1, pady=1, sticky="w")
            if i == 7:
                cols[i].grid(row=self.row, column=i, padx=1, pady=1, sticky="ew")
            else:
                cols[i].grid(
                    row=self.row,
                    column=i,
                    padx=1,
                    pady=1,
                )

    def removeFromProject(self):
        msg = f"You are about to delete {self.test.name.get()} from {self.project.name.get()}."
        msg += "\nThis will become permanent once you save the project. \nDo you wish to continue?"
        remove = messagebox.askyesno("Delete test", msg)
        if remove and self.test in self.project.tests:
            self.project.tests.remove(self.test)
            self.parent.master.build()
