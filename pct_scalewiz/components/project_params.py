"""Editor for Project params."""

from tkinter import ttk

# todo #6 implement some form of entry validation targeting non-whole number inputs (or make allowances for doubles)


class ProjectParams(ttk.Frame):
    """A form for mutating experiment-relevant attributes of the Project."""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)

        # row 0 ---------------------------------------------------------------
        bicarbLbl = ttk.Label(self, text="Bicarbonates (mg/L):")
        bicarbEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.bicarbs, from_=0, to=999999
        )
        parent.render(bicarbLbl, bicarbEnt, 0)

        # row 1 ---------------------------------------------------------------
        incrLbl = ttk.Label(self, text="Bicarbonates increased:")
        entFrm = ttk.Frame(self)
        entFrm.grid_columnconfigure(0, weight=1)
        entFrm.grid_columnconfigure(1, weight=1)
        foo = parent.editorProject.bicarbsIncreased
        ttk.Radiobutton(entFrm, text="Yes", variable=foo, value=True).grid(
            row=0, column=0
        )
        ttk.Radiobutton(entFrm, text="No", variable=foo, value=False).grid(
            row=0, column=1
        )
        parent.render(incrLbl, entFrm, 1)

        # row 2 ---------------------------------------------------------------
        chlorLbl = ttk.Label(self, text="Chlorides (mg/L):")
        chlorEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.chlorides, from_=0, to=999999
        )
        parent.render(chlorLbl, chlorEnt, 2)

        # row 3 ---------------------------------------------------------------
        tempLbl = ttk.Label(self, text="Test temperature (°F):")
        tempEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.temperature, from_=0, to=9999
        )
        parent.render(tempLbl, tempEnt, 3)

        # row 4 ---------------------------------------------------------------
        baselineLbl = ttk.Label(self, text="Baseline pressure (PSI):")
        baselineEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.baseline, from_=0, to=9999
        )
        parent.render(baselineLbl, baselineEnt, 4)

        # row 5 ---------------------------------------------------------------
        maxLbl = ttk.Label(self, text="Limiting pressure (PSI):")
        maxEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.limitPSI, from_=0, to=9999
        )
        parent.render(maxLbl, maxEnt, 5)

        # row 6 ---------------------------------------------------------------
        timeLbl = ttk.Label(self, text="Time limit (min.):")
        timeEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.limitMin, from_=0, to=9999
        )
        parent.render(timeLbl, timeEnt, 6)

        # row 7 ---------------------------------------------------------------
        freqLbl = ttk.Label(self, text="Reading interval (s):")
        freqEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.interval, from_=0, to=9999
        )
        parent.render(freqLbl, freqEnt, 7)

        # row 8 ---------------------------------------------------------------
        uptakeLbl = ttk.Label(self, text="Uptake time (s):")
        uptakeEnt = ttk.Spinbox(
            self, textvariable=parent.editorProject.uptake, from_=0, to=9999
        )
        parent.render(uptakeLbl, uptakeEnt, 8)
