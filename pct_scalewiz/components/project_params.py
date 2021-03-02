"""Editor for Project params."""

from tkinter import ttk

# todo #6 implement some form of entry validation
# targeting non-whole number inputs (or make allowances for doubles)


class ProjectParams(ttk.Frame):
    """A form for mutating experiment-relevant attributes of the Project."""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Bicarbonates (mg/L):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.bicarbs, from_=0, to=999999
        )
        parent.render(lbl, ent, 0)

        # row 1 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Bicarbonates increased:")
        ent = ttk.Frame(self)
        ent.grid_columnconfigure(0, weight=1)
        ent.grid_columnconfigure(1, weight=1)
        ttk.Radiobutton(
            ent, text="Yes", variable=parent.editorProject.bicarbs_increased, value=True
        ).grid(row=0, column=0)
        ttk.Radiobutton(
            ent, text="No", variable=parent.editorProject.bicarbs_increased, value=False
        ).grid(row=0, column=1)
        parent.render(lbl, ent, 1)

        # row 2 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Chlorides (mg/L):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.chlorides, from_=0, to=999999
        )
        parent.render(lbl, ent, 2)

        # row 3 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Test temperature (°F):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.temperature, from_=0, to=9999
        )
        parent.render(lbl, ent, 3)

        # row 4 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Baseline pressure (PSI):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.baseline, from_=0, to=9999
        )
        parent.render(lbl, ent, 4)

        # row 5 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Limiting pressure (PSI):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.limit_psi, from_=0, to=9999
        )
        parent.render(lbl, ent, 5)

        # row 6 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Time limit (min.):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.limit_minutes, from_=0, to=9999
        )
        parent.render(lbl, ent, 6)

        # row 7 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Reading interval (s):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.interval, from_=0, to=9999
        )
        parent.render(lbl, ent, 7)

        # row 8 ---------------------------------------------------------------
        lbl = ttk.Label(self, text="Uptake time (s):")
        ent = ttk.Spinbox(
            self, textvariable=parent.editorProject.uptake, from_=0, to=9999
        )
        parent.render(lbl, ent, 8)
