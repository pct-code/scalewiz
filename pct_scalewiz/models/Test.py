"""Model object for a Test."""

# util
import tkinter as tk


class Test:
    """
    Object for holding all the data associated with a Test.
    Basically a dict of tkVars.
    """

    def __init__(self) -> None:
        # serializable props
        self.is_blank = tk.BooleanVar()
        self.name = tk.StringVar()
        self.chemical = tk.StringVar()
        self.rate = tk.IntVar()
        self.reportAs = tk.StringVar()
        self.clarity = tk.StringVar()
        self.notes = tk.StringVar()
        self.toConsider = tk.StringVar()
        self.result = tk.DoubleVar()
        self.includeOnRep = tk.BooleanVar()
        self.readings = []
        self.maxPSI = tk.IntVar()
        self.obsBaseline = tk.IntVar()

        self.chemical.trace("w", self.makeName)
        self.rate.trace("w", self.makeName)
        self.name.trace("w", self.makeRepAs)
        self.toConsider.trace("w", self.getObsPSI)

        # todo abstract this out to some TOML
        self.toConsider.set("pump 1")
        self.is_blank.set(True)

    def makeName(self, _) -> None:
        if not (self.chemical.get() == "" or self.rate.get() == 0):
            self.name.set(f"{self.chemical.get()} {self.rate.get()} ppm")

    def makeRepAs(self, _) -> None:
        self.reportAs.set(self.name.get())

    def getObsPSI(self, *args) -> None:
        pressures = [
            self.readings[i][self.toConsider.get()] for i in range(len(self.readings))
        ]
        if not len(pressures) == 0:
            self.maxPSI.set(max(pressures))
            baselines = pressures[0:4]
            self.obsBaseline.set(round(sum(baselines) / 5))

    def dumpJson(self) -> dict:
        return {
            "name": self.name.get(),
            "isBlank": self.is_blank.get(),
            "chemical": self.chemical.get(),
            "rate": self.rate.get(),
            "reportAs": self.reportAs.get(),
            "clarity": self.clarity.get(),
            "notes": self.notes.get(),
            "toConsider": self.toConsider.get(),
            "includeOnRep": self.includeOnRep.get(),
            "result": self.result.get(),
            "obsBaseline": self.obsBaseline.get(),
            "readings": self.readings,
        }

    def loadJson(self, obj: dict) -> None:
        self.name.set(obj["name"])
        self.is_blank.set(obj["isBlank"])
        self.chemical.set(obj["chemical"])
        self.rate.set(obj["rate"])
        self.reportAs.set(obj["reportAs"])
        self.clarity.set(obj["clarity"])
        self.notes.set(obj["notes"])
        self.toConsider.set(obj["toConsider"])
        self.includeOnRep.set(obj["includeOnRep"])
        self.result.set(obj["result"])
        self.readings = obj["readings"]
        self.getObsPSI()

    def getReadings(self) -> list[int]:
        result = []
        for reading in self.readings:
            result.append(reading[self.toConsider.get()])
        return result
