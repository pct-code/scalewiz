"""Tkinter-powered model object for a Test, with some dict-related capabilities."""

from __future__ import annotations

# util
import logging
import tkinter as tk
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple, Union
    from uuid import UUID

LOGGER = logging.getLogger("scalewiz")


@dataclass
class Reading:
    """Holds the data for a particular reading."""

    elapsed_min: float
    pump1: int
    pump2: int
    average: int = round((pump1 + pump2) / 2)


#  this is currently unused
@dataclass
class TestData:
    name: str
    label: str
    is_blank: bool
    on_report: bool
    clarity: str
    readings: List[Reading]
    max_pressure: int
    observed_baseline: int
    pump_to_score: str
    result: float
    chemical: str
    rate: Union[float, int]


class Test:
    """Object for holding all the data associated with a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, data: dict = None) -> None:
        # mutable metadata
        self.is_blank = tk.BooleanVar()  # boolean for blank vs chemical trial
        self.name = tk.StringVar()  # identifier for the test
        self.chemical = tk.StringVar()  # chemical, if any, to be tested
        self.rate = tk.DoubleVar()  # the treating rate of the test
        self.label = tk.StringVar()  # how the test will be labeled on the report/plot
        self.clarity = tk.StringVar()  # the clarity of the treated water
        self.notes = tk.StringVar()  # misc notes on the experiment
        # immutable data
        self.readings: Tuple[Reading] = ()  # list of flat reading dicts
        self.uuid: UUID = None
        # mutable data
        self.pump_to_score = tk.StringVar()  # which series of PSIs to use
        self.result = tk.DoubleVar()  # represents the test's performance vs the blank
        self.include_on_report = tk.BooleanVar()  # condition for scoring
        self.max_psi = tk.IntVar()  # the highest psi of the test
        self.observed_baseline = tk.IntVar()  # a guess at the baseline for the test
        # set defaults
        self.pump_to_score.set("pump1")
        self.is_blank.set(True)
        self.add_traces()  # will need to clean these up later for the GC

        if isinstance(data, dict):
            self.load_json(data)

    def add_traces(self) -> None:
        """Adds tkVar traces. Need to be removed with remove_traces."""
        self.chemical.trace_add("write", self.update_test_name)
        self.rate.trace_add("write", self.update_test_name)
        self.name.trace_add("write", self.update_label)
        self.pump_to_score.trace_add("write", self.update_obs_baseline)

    def to_dict(self) -> dict[str, Union[bool, float, int, str]]:
        """Returns a dict representation of a Test."""
        self.strip_test()  # strip whitespaces from relevant fields
        # cast all readings from dataclasses to dicts
        readings = []
        for reading in self.readings:
            readings.append(
                {
                    "average": reading.average,
                    "pump1": reading.pump1,
                    "pump2": reading.pump2,
                    "elapsedMin": reading.elapsedMin,
                }
            )

        return {
            "name": self.name.get(),
            "is_blank": self.is_blank.get(),
            "chemical": self.chemical.get(),
            "rate": self.rate.get(),
            "report_as": self.label.get(),
            "clarity": self.clarity.get(),
            "notes": self.notes.get(),
            "to_consider": self.pump_to_score.get(),
            "include_on_report": self.include_on_report.get(),
            "result": self.result.get(),
            "observed_baseline": self.observed_baseline.get(),
            "readings": readings,
        }

    def load_json(self, obj: dict) -> None:
        """Load a Test with values from a dict."""
        # look for fallbacks for backwards compatability
        self.name.set(obj.get("name"))
        self.is_blank.set(obj.get("is_blank", obj.get("isBlank")))
        self.calcium.set(obj.get("calcium"))
        self.chemical.set(obj.get("chemical"))
        self.rate.set(obj.get("rate"))
        self.label.set(obj.get("report_as", obj.get("reportAs")))
        self.clarity.set(obj.get("clarity"))
        self.notes.set(obj.get("notes"))
        self.pump_to_score.set(obj.get("to_consider", obj.get("toConsider")))
        self.include_on_report.set(
            obj.get("include_on_report", obj.get("includeOnRep"))
        )
        self.result.set(obj.get("result"))
        readings: List[dict] = obj.get("readings")
        for reading in readings:
            # do some cleaning for backwards compatibility
            pump1 = reading.get("pump1", reading.get("pump 1"))
            pump2 = reading.get("pump2", reading.get("pump 2"))
            if "average" not in reading.keys():
                average = round((pump1 + pump2) / 2)
            self.readings.append(
                Reading(
                    average=average,
                    pump1=pump1,
                    pump2=pump2,
                    elapsed_min=reading.get("elapsed_min", reading.get("elapsedMin")),
                )
            )
        self.update_obs_baseline()

    def get_readings(self) -> Tuple[int]:
        """Returns a list of the pump_to_score's pressure readings."""
        pump = self.pump_to_score.get()
        if " " in pump:  # legacy accomodation for spaces in keys
            pump = pump.replace(" ", "")
        return tuple([getattr(reading, pump) for reading in self.readings])

    def update_test_name(self, *args) -> None:
        """Makes a name by concatenating the chemical name and rate."""
        if self.chemical.get() != "" and self.rate.get() != 0:
            if float(self.rate.get()) == int(self.rate.get()):
                self.name.set(f"{self.chemical.get()} {self.rate.get():.0f} ppm")
            else:
                self.name.set(f"{self.chemical.get()} {self.rate.get():.2f} ppm")

    def strip_test(self) -> None:
        """Do some formatting on the test to clean it up for storing."""
        strippables = (self.chemical, self.name, self.label, self.clarity, self.notes)
        for attr in strippables:
            val = attr.get()
            stripped = val.strip()
            if val != stripped:
                attr.set(stripped)

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
