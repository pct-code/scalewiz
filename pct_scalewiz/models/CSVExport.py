import logging
import tkinter 
from tkinter import messagebox
import os
from datetime import datetime
import PIL
import pandas as pd

from models.Project import Project

logger = logging.getLogger('scalewiz')


def export(proj: Project):
    logger.info(f"Beginning export of {project.name.get()}")

    out = f"{project.numbers.get().replace(' ', '')} {project.name.get()} - CaCO3 Scale Block Analysis.xlsx"
    out = os.path.join(os.path.dirname(project.path.get()), out)

    # select the blanks
    blanks = []
    for test in project.tests:
        if test.isBlank.get() and test.includeOnRep.get():
            blanks.append(test)
    
    blank_times = []
    i = project.interval.get()
    for blank in blanks:
        blank_times.append(len(blank.readings) * i)

    # select the trials
    trials = []
    for test in project.tests:
        if test.includeOnRep.get() and not test.isBlank.get():
            trials.append(test)

    chemicals = [trial.chemical.get() for trial in trials]
    rates = [trial.rate.get() for trial in trials]
    results = [trial.result.get() for trial in trials]
    durations = [round(len(trial.readings) * project.interval.get() / 60, 2) for trial in trials]
    baseline = project.baseline.get()
    ylim = project.limitPSI.get()
    max_psis = [trial.maxPSI.get() for trial in trials]
    clarities = [trial.clarity.get() for trial in trials]

    brine_comp = f"Synthetic Field Brine, Chlorides = {project.chlorides.get():,} mg/L"
    if project.bicarbsIncreased.get():
        brine_comp += f" (Bicarbs increased to {project.bicarbs.get():,} mg/L)"