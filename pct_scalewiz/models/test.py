"""Model object for a Test."""

# util
import tkinter as tk


class Test:
    """Object for holding all the data associated with a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        self.is_blank = tk.BooleanVar() # boolean for blank vs chemical trial
        self.name = tk.StringVar() # identifier for the test
        self.chemical = tk.StringVar() # chemical, if any, to be tested
        self.rate = tk.IntVar() # the treating rate of the test
        self.label = tk.StringVar() # how the test will be labeled on the report/plot
        self.clarity = tk.StringVar() # the clarity of the treated water
        self.notes = tk.StringVar() # misc notes on the experiment
        self.pump_to_score = tk.StringVar() # which series of PSIs to use
        self.result = tk.DoubleVar() # represents the test's performance vs the blank
        self.include_on_report = tk.BooleanVar() # condition for scoring
        self.readings: list[dict] = [] # list of flat reading dicts
        self.max_psi = tk.IntVar() # the highest psi of the test
        self.observed_baseline = tk.IntVar() # a guess at the baseline for the test
        # set defaults
        self.pump_to_score.set("pump 1")
        self.is_blank.set(True)
        self.add_traces()  # will need to clean these up later for the GC

    def add_traces(self) -> None:
        """Adds tkVar traces. Need to be removed with remove_traces."""
        self.chemical.trace_add("write", self.make_name)
        self.rate.trace_add("write", self.make_name)
        self.name.trace_add("write", self.make_label)
        self.pump_to_score.trace_add("write", self.set_observed_baseline)

    def to_dict(self) -> dict:
        """Returns a dict representation of a Test."""
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
            "readings": self.readings,
        }

    def load_json(self, obj: dict) -> None:
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
        self.readings = obj.get("readings")
        self.set_observed_baseline()

    def get_readings(self) -> list[int]:
        """Returns a list of the pump_to_score's pressure readings."""
        return [reading[self.pump_to_score.get()] for reading in self.readings]

    def make_name(self, *args) -> None:
        """Makes a name by concatenating the chemical name and rate."""
        if not (self.chemical.get() == "" or self.rate.get() == 0):
            self.name.set(f"{self.chemical.get()} {self.rate.get()} ppm")

        if self.chemical.get().strip() != self.chemical.get():
            self.chemical.set(self.chemical.get().strip())

    def make_label(self, *args) -> None:
        """Sets the label to the current name as a default value."""
        self.label.set(self.name.get().strip())

    def set_observed_baseline(self, *args) -> None:
        """Sets the observed baseline psi."""
        pressures = [reading[self.pump_to_score.get()] for reading in self.readings]
        if len(pressures) > 0:
            self.max_psi.set(max(pressures))
            baselines = pressures[0:4]
            self.observed_baseline.set(round(sum(baselines) / 4))

    def remove_traces(self) -> None:
        """Remove tkVar traces to allow the GC to do its thing."""
        self.chemical.trace_remove("write", self.chemical.trace_info()[0][1])
        self.rate.trace_remove("write", self.rate.trace_info()[0][1])
        self.name.trace_remove("write", self.name.trace_info()[0][1])
        self.pump_to_score.trace_remove("write", self.pump_to_score.trace_info()[0][1])
