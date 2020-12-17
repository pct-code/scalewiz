"""Component for displaying a Test in a gridlike fashion."""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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
        cols.append(ttk.Entry(self.parent, textvariable=self.test.reportAs, width=25))
        # col 2 - duration
        duration = len(self.test.readings) * self.project.interval.get() / 60
        cols.append(ttk.Label(self.parent, text=f"{duration:.2f}", anchor='center'))
        # col 3 - to consider
        cols.append(ttk.Combobox(self.parent, textvariable=self.test.toConsider, values=["pump 1", "pump 2", "average"], state='readonly', width=7))
        # col 4 - obs baseline
        cols.append(ttk.Label(self.parent, textvariable=self.test.obsBaseline, anchor='center'))
        # col 5 - max psi
        cols.append(ttk.Label(self.parent, textvariable=self.test.maxPSI, anchor='center'))
        # col 6 - clarity
        cols.append(ttk.Label(self.parent, textvariable=self.test.clarity, anchor='center'))
        # col 7 - notes
        self.grid_columnconfigure(6, weight=1)
        cols.append(ttk.Entry(self.parent, textvariable=self.test.notes))
        # col 8 - result
        cols.append(ttk.Label(self.parent, textvariable=self.test.result, anchor='center'))
        # col 9 - on report
        cols.append(ttk.Checkbutton(self.parent, variable=self.test.includeOnRep))
        # col 10 - delete
        cols.append(ttk.Button(self.parent, command=lambda: self.removeFromProject(), text="Delete", width=7))

        for i in range(len(cols)):
            if i == 0:
                cols[i].grid(row=self.row, column=i, padx=1, pady=1, sticky='w')
            else:
                cols[i].grid(row=self.row, column=i, padx=1, pady=1, )
    
    def removeFromProject(self, *args):
        msg = f"You are about to delete {self.test.name.get()} from {self.project.name.get()}."
        msg += "\nThis will become permanent once you save the project. \nDo you wish to continue?"
        remove = messagebox.askyesno("Delete test", msg)
        if remove and self.test in self.project.tests:
                self.project.tests.remove(self.test)
                self.parent.master.build()

