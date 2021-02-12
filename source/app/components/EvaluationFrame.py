"""Evaluation window for a Project."""

COLORS = "orange, blue, red, mediumseagreen, darkgoldenrod, indigo, mediumvioletred, darkcyan, maroon, darkslategrey".split(', ')

import os
import time
import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk, font
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator

from .BaseFrame import BaseFrame
from .TestResultRow import TestResultRow
from .ProjectInfo import ProjectInfo
from .ProjectParams import ProjectParams
from .ProjectReport import ProjectReport
from ..models.Project import Project
from ..models.Export import export_report

class EvaluationFrame(BaseFrame):
    def __init__(self, parent, handler):
        BaseFrame.__init__(self, parent)
        self.handler = handler 
        self.project = Project.loadJson(handler.project.path.get())
        self.editorProject = self.project
        parent.winfo_toplevel().title(self.project.name.get())
        self.build()

    def trace(self):
        for test in self.project.tests:
            test.reportAs.trace('w', self.score)
            test.toConsider.trace('w', self.score)
            test.includeOnRep.trace('w', self.score)

    def render(self, label, entry, row):
        label.grid(row=row, column=0, sticky='e')
        entry.grid(row=row, column=1, sticky='new', padx=(5, 550), pady=2)

    def build(self):
        for child in self.winfo_children():
            child.destroy()

        self.tabControl = ttk.Notebook(self)
        self.tabControl.grid(row=0, column=0)
        # col config this too?

        testsFrm = ttk.Frame(self)
        
        bold_font = font.Font(family="Arial", weight='bold', size=10)
        # header row
        labels = []
        labels.append(tk.Label(testsFrm, text="Name", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Report as", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Minutes", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Pump", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Baseline", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Max", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Clarity", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Notes", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Result", font=bold_font))
        labels.append(tk.Label(testsFrm, text="Report", font=bold_font))
        for i, label in enumerate(labels):
            label.grid(row=0, column=i, padx=3, sticky='w')

        self.grid_columnconfigure(0, weight=1)
        # add traces for scoring
        self.trace()
        
        self.blanks = []
        for test in self.project.tests:
            if test.isBlank.get():
                self.blanks.append(test)
        
        # select the trials
        self.trials = []
        for test in self.project.tests:
            if not test.isBlank.get():
                self.trials.append(test)

        tk.Label(testsFrm, text="Blanks:", font=bold_font).grid(row=1, column=0, sticky='w', padx=3, pady=1)
        tk.Label(testsFrm, text="Trials:", font=bold_font).grid(row=2+len(self.blanks), column=0, sticky='w', padx=3, pady=1)
        
        for i, blank in enumerate(self.blanks):
            TestResultRow(testsFrm, blank, self.project, i+2).grid(row=i+1, column=0, sticky='w', padx=3, pady=1)
        for i, trial in enumerate(self.trials):
            TestResultRow(testsFrm, trial, self.project, i+len(self.blanks)+3).grid(row=i+len(self.blanks)+3, column=0, sticky='w', padx=3, pady=1)
        
        self.tabControl.add(testsFrm, text="   Data   ")
        
        # plot stuff ----------------------------------------------------------
        self.plot()

        # evaluation stuff ----------------------------------------------------
        logFrm = ttk.Frame(self)
        logFrm.grid_columnconfigure(0, weight=1)
        self.logText = tk.scrolledtext.ScrolledText(logFrm, background='white', state='disabled')
        self.logText.grid(sticky='ew')
        self.tabControl.add(logFrm, text="   Calculations   ")

        # info
        self.tabControl.add(ProjectInfo(self), text="   Project Info   ", sticky='nsew')
        # params
        self.tabControl.add(ProjectParams(self), text="   Experiment Parameters   ", sticky='nsew')
        # report settings
        self.tabControl.add(ProjectReport(self), text="   Report Settings  ", sticky='nsew')

            
        btnFrm = ttk.Frame(self)
        ttk.Button(btnFrm, text="Save", command=lambda: self.save(), width=10).grid(row=0, column=0, padx=5)
        ttk.Button(btnFrm, text="Export", command=lambda: export_report(self, self.project), width=10).grid(row=0, column=1, padx=5)
        btnFrm.grid(row=1, column=0, pady=5)
        # update results
        self.score()

    def plot(self):
        # close all pyplots to prevent memory leak
        plt.close('all')
        # get rid of our old plot tab if we have one
        if hasattr(self, 'pltFrm'):
            self.pltFrm.destroy()
        
        self.pltFrm = ttk.Frame(self.tabControl)
        self.fig, self.axis = plt.subplots(figsize=(7.5, 4), dpi=100)
        self.fig.patch.set_facecolor('#FAFAFA')
        plt.subplots_adjust(wspace=0, hspace=0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.pltFrm)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        with plt.style.context('bmh'):
            mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=COLORS)
            self.axis.grid(color='darkgrey', alpha=0.65, linestyle='-')
            self.axis.set_facecolor('w')
            self.axis.clear()

            # plot everything
            for blank in self.blanks:
                if blank.includeOnRep.get():
                    elapsed = []
                    for i, reading in enumerate(blank.readings):
                        elapsed.append(blank.readings[i]["elapsedMin"])
                    self.axis.plot(elapsed, blank.getReadings(), label=blank.reportAs.get(), linestyle=('-.'))
            
            for trial in self.trials:
                if trial.includeOnRep.get():
                    elapsed = []
                    for i, reading in enumerate(trial.readings):
                        elapsed.append(trial.readings[i]["elapsedMin"])
                    self.axis.plot(elapsed, trial.getReadings(), label=trial.reportAs.get())
            
            self.axis.set_xlabel("Time (min)")
            self.axis.set_ylabel("Pressure (psi)")
            self.axis.set_ylim(top=self.project.limitPSI.get())
            self.axis.yaxis.set_major_locator(MultipleLocator(100))
            self.axis.set_xlim((0, self.project.limitMin.get()))
            self.axis.legend(loc=0)
            self.axis.margins(0)
            plt.tight_layout()
           
            
        # finally, add to parent control
        self.tabControl.add(self.pltFrm, text="   Plot   ")
        self.tabControl.insert(1, self.pltFrm)

    def save(self):
        # update image 
        out = f"{self.project.numbers.get().replace(' ', '')} {self.project.name.get()} Scale Block Analysis (Graph).png"
        out = os.path.join(os.path.dirname(self.project.path.get()), out)
        self.fig.savefig(out)
        self.project.plot.set(out)
        # update log 
        out = f"{self.project.numbers.get().replace(' ', '')} {self.project.name.get()} Scale Block Analysis (Log).txt"
        out = os.path.join(os.path.dirname(self.project.path.get()), out)
        log = self.logText.get("1.0",'end-1c')
        with (open(out, 'w') as file):
            file.write(log)
        
        Project.dumpJson(self.project, self.project.path.get())
        self.handler.project = Project.loadJson(self.project.path.get())
        self.project = self.handler.project
        self.editorProject = self.project
        
        # how about a call to build instead?
        self.build()

    def score(self, *args):
        startTime = time.time()
        self.log = []
        # scoring props
       
        maxReadings = round(self.project.limitMin.get() * 60 / self.project.interval.get())
        self.log.append(f"Max readings: limitMin * 60 / reading interval")
        self.log.append(f"Max readings: {maxReadings}")
        baselineArea = round(self.project.baseline.get() * maxReadings)
        self.log.append(f"Baseline area: baseline PSI * max readings")
        self.log.append(f"Baseline area: {self.project.baseline.get()} * {maxReadings}")
        self.log.append(f"Baseline area: {baselineArea}")
        self.log.append("-"*80)
        self.log.append("")

        # select the blanks
        blanks = []
        for test in self.project.tests:
            if (test.isBlank.get() and test.includeOnRep.get()):
                blanks.append(test)

        if len(blanks) < 1:
            return

        areasOverBlanks = []
        for blank in blanks:
            self.log.append(f"Evaluating {blank.name.get()}")
            self.log.append(f"Considering data: {blank.toConsider.get()}")
            readings = blank.getReadings()
            self.log.append(f"Total readings: {len(readings)}")
            intPSI = sum(readings)
            self.log.append(f"Integral PSI: sum of all pressure readings")
            self.log.append(f"Integral PSI: {intPSI}")
            area = self.project.limitPSI.get() * len(readings) - intPSI
            self.log.append(f"Area over blank: limitPSI * # of readings - integral PSI")
            self.log.append(f"Area over blank: {self.project.limitPSI.get()} * {len(readings)} - {intPSI}")
            self.log.append(f"Area over blank: {area}")
            self.log.append("")
            areasOverBlanks.append(area)

        # get protectable area
        avgBlankArea = round(sum(areasOverBlanks) / len(areasOverBlanks)) 
        self.log.append(f"Average area over blanks: {avgBlankArea}")
        avgProtectableArea = self.project.limitPSI.get() * maxReadings - avgBlankArea
        self.log.append(f"Average protectable area: limitPSI * maxReadings - average area over blanks")
        self.log.append(f"Average protectable area: {self.project.limitPSI.get()} * {maxReadings} - {avgBlankArea}")
        self.log.append(f"Average protectable area: {avgProtectableArea}")
        self.log.append("-"*80)
        self.log.append("")


        # select trials
        trials = []
        for test in self.project.tests:
            if not test.isBlank.get():
                trials.append(test)

        # get readings
        for trial in trials:
            self.log.append(f"Evaluating {trial.name.get()}")
            self.log.append(f"Considering data: {trial.toConsider.get()}")
            readings = trial.getReadings()
            self.log.append(f"Total readings: {len(readings)}")
            intPSI = sum(readings) + ((maxReadings - len(readings)) * self.project.limitPSI.get())
            self.log.append(f"Integral PSI: sum of all pressure readings")
            self.log.append(f"Integral PSI: {intPSI}")
            result = round(1 - (intPSI - baselineArea) / avgProtectableArea, 3)
            self.log.append(f"Result: 1 - (integral PSI - baseline area) / avg protectable area")
            self.log.append(f"Result: 1 - ({intPSI} - {baselineArea}) / {avgProtectableArea}")
            self.log.append(f"Result: {result}")
            self.log.append("")
            trial.result.set(result)

        self.plot()
        self.log.append("-"*80)
        t = round(time.time() - startTime, 3) 

        self._log = self.log
        self.log = []
        self.log.append(f"Evaluating results for {self.project.name.get()}...")
        self.log.append("")
        self.log.append(f"Finished in {t} s")
        self.log.append("-"*80)
        self.log.append("")
        for msg in self._log:
            self.log.append(msg)
        self.toLog(self.log)

    def toLog(self, log):
        self.logText.configure(state='normal')
        self.logText.delete(1.0, 'end')
        for i in log:
            self.logText.insert('end', i)
            self.logText.insert('end', "\n")
        self.logText.configure(state='disabled')
        