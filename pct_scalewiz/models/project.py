"""Model object for a project. Provides a JSON/Tk mapping."""

from __future__ import annotations

import json
import logging
import os
import tkinter as tk

from pct_scalewiz.helpers.sort_nicely import sort_nicely
from pct_scalewiz.models.test import Test

logger = logging.getLogger("scalewiz")


class Project:
    """Model object for a project. Provides a JSON/tkVar mapping."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        # serializable test info
        self.customer = tk.StringVar()
        self.submitted_by = tk.StringVar()
        self.client = tk.StringVar()
        self.field = tk.StringVar()
        self.sample = tk.StringVar()

        self.sample_date = tk.StringVar()
        self.received_date = tk.StringVar()
        self.completed_date = tk.StringVar()
        self.name = tk.StringVar()
        self.analyst = tk.StringVar()
        self.numbers = tk.StringVar()
        self.path = tk.StringVar()
        self.notes = tk.StringVar()
        # serializable test params
        self.bicarbs = tk.IntVar()
        self.bicarbs_increased = tk.BooleanVar()
        self.chlorides = tk.IntVar()
        self.baseline = tk.IntVar()
        self.temperature = tk.IntVar()
        self.limit_psi = tk.IntVar()
        self.limit_minutes = tk.IntVar()
        self.interval = tk.IntVar()
        self.uptake = tk.IntVar()
        # report stuff
        self.output_format = tk.StringVar()
        self.plot = tk.StringVar()

        self.tests: list[dict] = []

        # maintain live fields
        self.customer.trace_add("write", self.make_name)
        self.client.trace_add("write", self.make_name)
        self.field.trace_add("write", self.make_name)
        self.sample.trace_add("write", self.make_name)

        # set defaults
        # todo #3 abstract these out into some TOML or something

        self.baseline.set(75)
        self.limit_psi.set(1500)
        self.limit_minutes.set(90)
        self.interval.set(3)
        self.uptake.set(60)
        # todo clean out this old template stuff ?
        self.output_format.set("CSV")

    def make_name(self, *args) -> None:
        """Constructs a default name for the Project."""
        # extra unused args are passed in by tkinter
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

    def dump_json(self, path=None) -> None:
        """Dump a JSON representation of the Project at the passed path."""
        if path is None:
            path = self.path.get()

        for test in self.tests:
            if test.chemical.get().strip() != test.chemical.get():
                test.chemical.set(test.chemical.get().strip())

            if test.label.get().strip() != test.label.get():
                test.label.set(test.label.get().strip())

        # filter the data alphanumerically by label
        _blanks = {}  # put in dicts to allow for popping later
        _trials = {}
        keys = []
        for test in self.tests:
            key = test.label.get().lower()  # eliminate capitalization discrepancies
            while key in keys:  # checking for duplicate values
                test.label.set(test.label.get() + " - copy")
                key = test.label.get().lower()

            keys.append(key)

            if test.is_blank.get():
                _blanks[key] = test
            else:
                _trials[key] = test

        blank_labels = sort_nicely(
            [blank.label.get().lower() for blank in list(_blanks.values())]
        )
        blanks = [_blanks.pop(name) for name in blank_labels]

        # instead, sort by label then by conc magnitude
        trial_labels = sort_nicely(
            [trial.label.get().lower() for trial in list(_trials.values())]
        )
        trials = [_trials.pop(name) for name in trial_labels]

        self.tests = [*blanks, *trials]

        this = {
            "info": {
                "customer": self.customer.get(),
                "submittedBy": self.submitted_by.get(),
                "productionCo": self.client.get(),
                "field": self.field.get(),
                "sample": self.sample.get(),
                "sampleDate": self.sample_date.get(),
                "recDate": self.received_date.get(),
                "compDate": self.completed_date.get(),
                "name": self.name.get(),
                "analyst": self.analyst.get(),
                "numbers": self.numbers.get(),
                "path": os.path.abspath(self.path.get()),
                "notes": self.notes.get(),
            },
            "params": {
                "bicarbonates": self.bicarbs.get(),
                "bicarbsIncreased": self.bicarbs_increased.get(),
                "chlorides": self.chlorides.get(),
                "baseline": self.baseline.get(),
                "temperature": self.temperature.get(),
                "limitPSI": self.limit_psi.get(),
                "limitMin": self.limit_minutes.get(),
                "interval": self.interval.get(),
                "uptake": self.uptake.get(),
            },
            "tests": [test.dump_json() for test in self.tests],
            "outputFormat": self.output_format.get(),
            "plot": os.path.abspath(self.plot.get()),
        }

        with open(path, "w") as file:
            json.dump(this, file, indent=4)

        logger.info("Saved %s to %s", self.name.get(), path)

    def load_json(self, path: str) -> None:
        """Return a Project from a passed path to a JSON dump."""
        logger.info("Loading from %s", path)
        with open(path, "r") as file:
            obj = json.load(file)

        # we expect the data files to be shared over Dropbox, etc.
        if path != obj.get("info").get("path"):
            logger.warning(
                "Opened a Project whose actual path didn't match its path property"
            )
            obj["info"]["path"] = path

        info = obj.get("info")
        self.customer.set(info.get("customer"))
        self.submitted_by.set(info.get("submittedBy"))
        self.client.set(info.get("productionCo"))
        self.field.set(info.get("field"))
        self.sample.set(info.get("sample"))
        self.sample_date.set(info.get("sampleDate"))
        self.received_date.set(info.get("recDate"))
        self.completed_date.set(info.get("compDate"))
        self.name.set(info.get("name"))
        self.numbers.set(info.get("numbers"))
        self.analyst.set(info.get("analyst"))
        self.path.set(info.get("path"))
        self.notes.set(info.get("notes"))

        params = obj.get("params")
        self.bicarbs.set(params.get("bicarbonates"))
        self.bicarbs_increased.set(params.get("bicarbsIncreased"))
        self.chlorides.set(params.get("chlorides"))
        self.baseline.set(params.get("baseline"))
        self.temperature.set(params.get("temperature"))
        self.limit_psi.set(params.get("limitPSI"))
        self.limit_minutes.set(params.get("limitMin"))
        self.interval.set(params.get("interval"))
        self.uptake.set(params.get("uptake"))

        self.plot.set(obj.get("plot"))
        self.output_format.set(obj.get("outputFormat"))

        for entry in obj.get("tests"):
            test = Test()
            test.load_json(entry)
            self.tests.append(test)
