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
        self.tests: list[Test] = []
        # experiment parameters that affect score
        self.baseline = tk.IntVar()
        self.limit_minutes = tk.IntVar()
        self.limit_psi = tk.IntVar()
        self.interval = tk.IntVar()
        self.uptake = tk.IntVar()
        # report stuff
        self.output_format = tk.StringVar()
        # metadata for reporting
        self.customer = tk.StringVar()
        self.submitted_by = tk.StringVar()
        self.client = tk.StringVar()
        self.field = tk.StringVar()
        self.sample = tk.StringVar()
        self.sample_date = tk.StringVar()
        self.received_date = tk.StringVar()
        self.completed_date = tk.StringVar()
        self.name = tk.StringVar()  # identifier for the project
        self.analyst = tk.StringVar()
        self.numbers = tk.StringVar()
        self.path = tk.StringVar()  # path to the project's JSON file
        self.notes = tk.StringVar()
        self.bicarbs = tk.IntVar()
        self.bicarbs_increased = tk.BooleanVar()
        self.chlorides = tk.IntVar()
        self.temperature = tk.IntVar()  # the test temperature
        self.plot = tk.StringVar()  # path to plot local file
        # set defaults
        # todo #3 abstract these out into some TOML or something ?
        self.baseline.set(75)
        self.limit_psi.set(1500)
        self.limit_minutes.set(90)
        self.interval.set(3)
        self.uptake.set(60)
        self.output_format.set("CSV")
        self.add_traces()  # these need to be cleaned up later

    def add_traces(self) -> None:
        """Adds tkVar traces where needed. Must be cleaned up with remove_traces."""
        self.customer.trace_add("write", self.make_name)
        self.client.trace_add("write", self.make_name)
        self.field.trace_add("write", self.make_name)
        self.sample.trace_add("write", self.make_name)

    def dump_json(self, path=None) -> None:
        """Dump a JSON representation of the Project at the passed path."""
        if path is None:
            path = self.path.get()

        blanks = [test for test in self.tests if test.is_blank.get()]
        trials = [test for test in self.tests if not test.is_blank.get()]
        blank_labels = sort_nicely([test.label.get().lower() for test in blanks])
        trial_labels = sort_nicely([test.label.get().lower() for test in trials])
        tests = []
        for label in blank_labels:
            for test in self.tests:
                if test.label.get().lower() == label:
                    tests.append(test)

        for label in trial_labels:
            for test in self.tests:
                if test.label.get().lower() == label:
                    tests.append(test)

        self.tests.clear()
        for test in tests:
            self.tests.append(test)

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
            "tests": [test.to_dict() for test in self.tests],
            "outputFormat": self.output_format.get(),
            "plot": os.path.abspath(self.plot.get()),
        }

        with open(path, "w") as file:
            json.dump(this, file, indent=4)
            logger.info("Saved %s to %s", self.name.get(), path)

    def load_json(self, path: str) -> None:
        """Return a Project from a passed path to a JSON dump."""
        path = os.path.abspath(path)
        if os.path.isfile(path):
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

    def remove_traces(self) -> None:
        """Remove tkVar traces to allow the GC to do its thing."""
        vars = (self.customer, self.client, self.field, self.sample)
        for var in vars:
            # logger.debug(var.trace_info())
            var.trace_remove("write", var.trace_info()[0][1])

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
