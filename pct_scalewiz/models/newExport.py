import logging
import os
import time
import tkinter
from datetime import datetime
from tkinter import messagebox

import json
import pandas as pd
import PIL

from models.Project import Project

logger = logging.getLogger('scalewiz')

def export(proj: Project) -> None:
    """Generates a report for the passed Project in JSON format."""
    start_time = time.time()
    logger.info(f"Beginning export of {project.name.get()}")

    output = {
            "customer": project.customer.get(),
            "submitted by": project.submittedBy.get(),
            "prod. co": project.productionCo.get(),
            "field": project.field.get(),
            "analysis nos.": project.analysis.get(),
            "date sampled:" project.sampleDate.get(),
            "date received": project.recDate.get(),
            "date completed": project.compDate.get(),
            "test temp F": project.temperature.get().
            "baseline psi": project.baseline.get(),
            "bicarbs": project.bicarbs.get(),
            "bicarbs increase": project.bicarbsIncreased.get(),
            "chlorides": project.chlorides.get(),
            "time limit min": project.limitMin.get(),
            "max psi": project.limitPSI.get(),
            "blanks": {},
            "trials": {},
            "plot_path": project.plot.get()
        }

    # select the blanks
    blanks = []
    for test in project.tests:
        if test.isBlank.get() and test.includeOnRep.get():
            blanks.append(test)
    
    blank_times = []
    i = project.interval.get()
    for blank in blanks:
        blank_times.append(len(blank.readings) * i)

    # add to output dict
    for b, t in zip(blanks, blank_times):
        output["blanks"][b.reportAs.get()] = t    

    # select the trials
    trials = []
    for test in project.tests:
        if test.includeOnRep.get() and not test.isBlank.get():
            trials.append(test)

    chemicals = [trial.chemical.get() for trial in trials]
    rates = [trial.rate.get() for trial in trials]
    durations = [round(len(trial.readings) * project.interval.get() / 60, 2) for trial in trials]
    max_psis = [trial.maxPSI.get() for trial in trials]
    results = [trial.result.get() for trial in trials]
    clarities = [trial.clarity.get() for trial in trials]

    trial_data = zip(range(len(trials)), chemicals, rates, durations, max_psis, results, clarities)
    for idx, chemical, rate, result, duration, max_psi, clarity in trial_data:
        output["trials"][idx] = {
            "chemical": chemical,
            "rate": rate,
            "duration": duration,
            "max_psi": max_psi,
            "result": result,
            "clarity": clarity
        }

    out = f"{project.numbers.get().replace(' ', '')} {project.name.get()} - CaCO3 Scale Block Analysis.json"
    out = os.path.join(os.path.dirname(project.path.get()), out)
    json.dump(output, out)
    
    logger.info(f"Finished export of {project.name.get()} in {round(start_time - time.time(), 3)} s")
