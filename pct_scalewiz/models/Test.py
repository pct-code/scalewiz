"""Model object for a Test."""

# util
import tkinter as tk


class Test:
    """Object for holding all the data associated with a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        # serializable props
        self.is_blank = tk.BooleanVar()
        self.name = tk.StringVar()
        self.chemical = tk.StringVar()
        self.rate = tk.IntVar()
        self.label = tk.StringVar()
        self.clarity = tk.StringVar()
        self.notes = tk.StringVar()
        self.pump_to_score = tk.StringVar()
        self.result = tk.DoubleVar()
        self.include_on_report = tk.BooleanVar()
        self.readings = []
        self.max_psi = tk.IntVar()
        self.observed_baseline = tk.IntVar()

        self.chemical.trace("w", self.make_name)
        self.rate.trace("w", self.make_name)
        self.name.trace("w", self.make_label)
        self.pump_to_score.trace("w", self.set_observed_baseline)

        # todo abstract this out to some TOML
        self.pump_to_score.set("pump 1")
        self.is_blank.set(True)

    def make_name(self, *args) -> None:
        """Makes a name by concatenating the chemical name and rate."""
        if not (self.chemical.get() == "" or self.rate.get() == 0):
            self.name.set(f"{self.chemical.get()} {self.rate.get()} ppm")

    def make_label(self, *args) -> None:
        """Sets the label to the current name as a default value."""
        self.label.set(self.name.get())

    def set_observed_baseline(self, *args) -> None:
        """Sets the observed baseline psi."""
        pressures = [reading[self.pump_to_score.get()] for reading in self.readings]
        if len(pressures) > 0:
            self.max_psi.set(max(pressures))
            baselines = pressures[0:4]
            self.observed_baseline.set(round(sum(baselines) / 4))

    def dump_json(self) -> dict:
        """Returns a dict represendation of a Test."""
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
