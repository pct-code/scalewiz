"""Model object for a Test."""

from __future__ import annotations

# util
import logging
import tkinter as tk
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Union

LOGGER = logging.getLogger("scalewiz")


@dataclass
class Reading:
    elapsedMin: float
    pump1: int
    pump2: int
    average: int


class Test:
    """Object for holding all the data associated with a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        self.is_blank = tk.BooleanVar()  # boolean for blank vs chemical trial
        self.name = tk.StringVar()  # identifier for the test
        self.chemical = tk.StringVar()  # chemical, if any, to be tested
        self.rate = tk.DoubleVar()  # the treating rate of the test
        self.label = tk.StringVar()  # how the test will be labeled on the report/plot
        self.clarity = tk.StringVar()  # the clarity of the treated water
        self.notes = tk.StringVar()  # misc notes on the experiment
        self.pump_to_score = tk.StringVar()  # which series of PSIs to use
        self.result = tk.DoubleVar()  # represents the test's performance vs the blank
        self.include_on_report = tk.BooleanVar()  # condition for scoring
        self.readings: List[Reading] = []  # list of flat reading dicts
        self.max_psi = tk.IntVar()  # the highest psi of the test
        self.observed_baseline = tk.IntVar()  # a guess at the baseline for the test
        # set defaults
        self.pump_to_score.set("pump 1")
        self.is_blank.set(True)
        self.add_traces()  # will need to clean these up later for the GC

    def add_traces(self) -> None:
        """Adds tkVar traces. Need to be removed with remove_traces."""
        self.chemical.trace_add("write", self.update_test_name)
        self.rate.trace_add("write", self.update_test_name)
        self.name.trace_add("write", self.update_label)
        self.pump_to_score.trace_add("write", self.update_obs_baseline)

    def to_dict(self) -> dict[str, Union[bool, float, int, str]]:
        """Returns a dict representation of a Test."""
        self.clean_test()  # strip whitespaces from relevant fields
        # cast all readings from dataclasses to dicts
        readings = []
        for reading in self.readings:
            readings.append(
                {
                    "pump 1": reading.pump1,
                    "pump 2": reading.pump2,
                    "average": reading.average,
                    "elapsedMin": reading.elapsedMin,
                }
            )

        return {
            "name": self.name.get(),
            "isBlank": self.is_blank.get(),
            "chemical": self.chemical.get(),
            "rate": self.rate.get(),
            "reportAs": self.label.get(),
            "clarity": self.clarity.get(),
            "notes": self.notes.get(),
            "toConsider": self.pump_to_score.get(),
            "includeOnRep": self.include_on_report.get(),
            "result": self.result.get(),
            "obsBaseline": self.observed_baseline.get(),
            "readings": readings,
        }

    def load_json(self, obj: dict[str, Union[bool, float, int, str]]) -> None:
        """Load a Test with values from a JSON object."""
        self.name.set(obj.get("name"))
        self.is_blank.set(obj.get("isBlank"))
        self.chemical.set(obj.get("chemical"))
        self.rate.set(obj.get("rate"))
        self.label.set(obj.get("reportAs"))
        self.clarity.set(obj.get("clarity"))
        self.notes.set(obj.get("notes"))
        self.pump_to_score.set(obj.get("toConsider"))
        self.include_on_report.set(obj.get("includeOnRep"))
        self.result.set(obj.get("result"))
        readings = obj.get("readings")
        for reading in readings:
            self.readings.append(
                Reading(
                    pump1=reading["pump 1"],
                    pump2=reading["pump 2"],
                    average=reading["average"],
                    elapsedMin=reading["elapsedMin"],
                )
            )
        self.update_obs_baseline()

    def get_readings(self) -> List[int]:
        """Returns a list of the pump_to_score's pressure readings."""
        pump = self.pump_to_score.get()
        pump = pump.replace(" ", "")  # legacy accomodation for spaces in keys
        return [getattr(reading, pump) for reading in self.readings]

    def update_test_name(self, *args) -> None:
        """Makes a name by concatenating the chemical name and rate."""
        if not (self.chemical.get() == "" or self.rate.get() == 0):
            if float(self.rate.get()) == int(self.rate.get()):
                self.name.set(f"{self.chemical.get()} {self.rate.get():.0f} ppm")
            else:
                self.name.set(f"{self.chemical.get()} {self.rate.get():.2f} ppm")

    def clean_test(self) -> None:
        """Do some formatting on the test to clean it up for storing."""
        strippables = (self.chemical, self.name, self.label, self.clarity, self.notes)
        for attr in strippables:
            if attr.get().strip() != attr.get():
                attr.set(attr.get().strip())

    def update_label(self, *args) -> None:
        """Sets the label to the current name as a default value."""
        self.label.set(self.name.get().strip())

    def update_obs_baseline(self, *args) -> None:
        """Sets the observed baseline psi."""
        if len(self.readings) > 0:
            pressures = self.get_readings()
            self.max_psi.set(max(pressures))
            baselines = pressures[0:4]
            self.observed_baseline.set(round(sum(baselines) / 4))

    def remove_traces(self) -> None:
        """Remove tkVar traces to allow the GC to do its thing."""
        variables = (self.chemical, self.rate, self.name, self.pump_to_score)
        for var in variables:
            try:
                var.trace_remove("write", var.trace_info()[0][1])
            except IndexError:  # sometimes this spaghets on empty projects...
                pass
