"""Model object for a project. Provides a JSON/Tk mapping."""
import json
import logging
import os
import tkinter as tk

from pct_scalewiz.helpers.get_resource import get_resource
from pct_scalewiz.helpers.sort_nicely import sort_nicely
from pct_scalewiz.models.test import Test

logger = logging.getLogger("scalewiz")


class Project:
    """Model object for a project. Provides a JSON/tkVar mapping."""

    def __init__(self) -> None:
        # serializable test info
        self.customer = tk.StringVar()
        self.submitted_by = tk.StringVar()
        self.client = tk.StringVar()
        self.field = tk.StringVar()
        self.sample = tk.StringVar()

        self.sample_date = tk.StringVar()
        self.received_date = tk.StringVar()
        self.compDate = tk.StringVar()
        self.name = tk.StringVar()
        self.analyst = tk.StringVar()
        self.numbers = tk.StringVar()
        self.path = tk.StringVar()
        self.notes = tk.StringVar()
        # serializable test params
        self.bicarbs = tk.IntVar()
        self.bicarbsIncreased = tk.BooleanVar()
        self.chlorides = tk.IntVar()
        self.baseline = tk.IntVar()
        self.temperature = tk.IntVar()
        self.limit_psi = tk.IntVar()
        self.limitMin = tk.IntVar()
        self.interval = tk.IntVar()
        self.uptake = tk.IntVar()
        # report stuff
        self.output_format = tk.StringVar()
        self.plot = tk.StringVar()

        # list of JSON objects
        self.tests = []

        # maintain live fields
        self.customer.trace("w", self.makeName)
        self.client.trace("w", self.makeName)
        self.field.trace("w", self.makeName)
        self.sample.trace("w", self.makeName)

        # set defaults
        # todo #3 abstract these out into some TOML or something

        self.baseline.set(75)
        self.limit_psi.set(1500)
        self.limitMin.set(90)
        self.interval.set(3)
        self.uptake.set(60)
        # todo clean out this old template stuff ?
        self.output_format.set("CSV")

    def makeName(self, _) -> None:
        """Constructs a default name for the Project."""
        name = ""
        if self.client.get() != "":
            name = self.client.get().strip()
        else:
            name = self.customer.get().strip()
        if self.field.get() != "":
            name = f"{name} - {self.field.get()}".strip()
        if self.sample.get() != "":
            name = f"{name} ({self.sample.get()})".strip()
        self.name.set(name)

    def trimNames(self) -> None:
        for test in self.tests:
            if test.chemical.get().strip() != test.chemical.get():
                test.chemical.set(test.chemical.get().strip())

            if test.reportAs.get().strip() != test.reportAs.get():
                test.reportAs.set(test.reportAs.get().strip())

    @staticmethod
    def dumpJson(project, path: str) -> None:
        project.trimNames()

        # filter the data alphanumerically by label
        _blanks = {}  # put in dicts to allow for popping later
        _trials = {}
        keys = []
        for test in project.tests:
            key = test.reportAs.get().lower()  # eliminate capitalization discrepancies
            while key in keys:  # checking for duplicate values
                test.reportAs.set(test.reportAs.get() + " - copy")
                key = test.reportAs.get().lower()

            keys.append(key)

            if test.is_blank.get():
                _blanks[key] = test
            else:
                _trials[key] = test

        blankNames = sort_nicely(
            [blank.reportAs.get().lower() for blank in list(_blanks.values())]
        )
        blanks = [_blanks.pop(name) for name in blankNames]

        # instead, sort by label then by conc magnitude
        trialNames = sort_nicely(
            [trial.reportAs.get().lower() for trial in list(_trials.values())]
        )
        trials = [_trials.pop(name) for name in trialNames]

        project.tests = [*blanks, *trials]

        this = {
            "info": {
                "customer": project.customer.get(),
                "submittedBy": project.submitted_by.get(),
                "productionCo": project.client.get(),
                "field": project.field.get(),
                "sample": project.sample.get(),
                "sampleDate": project.sample_date.get(),
                "recDate": project.received_date.get(),
                "compDate": project.compDate.get(),
                "name": project.name.get(),
                "analyst": project.analyst.get(),
                "numbers": project.numbers.get(),
                "path": os.path.abspath(project.path.get()),
                "notes": project.notes.get(),
            },
            "params": {
                "bicarbonates": project.bicarbs.get(),
                "bicarbsIncreased": project.bicarbsIncreased.get(),
                "chlorides": project.chlorides.get(),
                "baseline": project.baseline.get(),
                "temperature": project.temperature.get(),
                "limitPSI": project.limit_psi.get(),
                "limitMin": project.limitMin.get(),
                "interval": project.interval.get(),
                "uptake": project.uptake.get(),
            },
            "tests": [test.dumpJson() for test in project.tests],
            "outputFormat": project.output_format.get(),
            "plot": os.path.abspath(project.plot.get()),
        }

        with open(project.path.get(), "w") as file:
            json.dump(this, file, indent=4)

        logger.info("Saved %s to %s", project.name.get(), project.path.get())

    @staticmethod
    def loadJson(path) -> "Project":
        logger.info(f"Loading from {path}")
        with open(path, "r") as file:
            obj = json.load(file)

        this = Project()
        info = obj.get("info")
        this.customer.set(info.get("customer"))
        this.submitted_by.set(info.get("submittedBy"))
        this.client.set(info.get("productionCo"))
        this.field.set(info.get("field"))
        this.sample.set(info.get("sample"))
        this.sample_date.set(info.get("sampleDate"))
        this.received_date.set(info.get("recDate"))
        this.compDate.set(info.get("compDate"))
        this.name.set(info.get("name"))
        this.numbers.set(info.get("numbers"))
        this.analyst.set(info.get("analyst"))
        this.path.set(info.get("path"))
        this.notes.set(info.get("notes"))

        params = obj.get("params")
        this.bicarbs.set(params.get("bicarbonates"))
        this.bicarbsIncreased.set(params.get("bicarbsIncreased"))
        this.chlorides.set(params.get("chlorides"))
        this.baseline.set(params.get("baseline"))
        this.temperature.set(params.get("temperature"))
        this.limit_psi.set(params.get("limitPSI"))
        this.limitMin.set(params.get("limitMin"))
        this.interval.set(params.get("interval"))
        this.uptake.set(params.get("uptake"))

        this.plot.set(obj.get("plot"))
        this.output_format.set(obj.get("outputFormat"))

        for entry in obj.get("tests"):
            this.tests.append(Test().loadJson(entry))

        return this
