"""Model object for a Test."""

# util
import tkinter as tk

class Test:
    def __init__(self):
        # serializable props
        self.isBlank = tk.BooleanVar()
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

        self.chemical.trace('w', self.makeName)
        self.rate.trace('w', self.makeName)
        self.name.trace('w', self.makeRepAs)
        self.toConsider.trace('w', self.getObsPSI)

        # todo 
        self.toConsider.set('pump 1') # move this to config later
        self.isBlank.set(True)

    def makeName(self, *args):
        if not (
            self.chemical.get() == ""
            or self.rate.get() == 0
        ):
            self.name.set(f"{self.chemical.get()} {self.rate.get()} ppm")
    
    def makeRepAs(self, *args):
        self.reportAs.set(self.name.get())
    
    def getObsPSI(self, *args):
        pressures = [self.readings[i][self.toConsider.get()] for i in range(len(self.readings))]
        if not len(pressures) == 0:
            self.maxPSI.set(max(pressures))
            baselines = pressures[0:4]
            self.obsBaseline.set(round(sum(baselines) / 5))

    def dumpJson(self) -> dict:
        this = {
            "name": self.name.get(),
            "isBlank": self.isBlank.get(),
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
        return this
    
    def loadJson(self, obj):
        self.name.set(obj['name'])
        self.isBlank.set(obj['isBlank'])
        self.chemical.set(obj["chemical"])
        self.rate.set(obj['rate'])
        self.reportAs.set(obj['reportAs'])
        self.clarity.set(obj['clarity'])
        self.notes.set(obj['notes'])
        self.toConsider.set(obj['toConsider'])
        self.includeOnRep.set(obj['includeOnRep'])
        self.result.set(obj['result'])
        self.readings = obj['readings']
        self.getObsPSI()

    def getReadings(self) -> [int]:
        result = []
        for reading in self.readings:
            result.append(reading[self.toConsider.get()])
        return result
