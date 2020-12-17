"""Model object for a project. Provides a JSON/Tk mapping."""

import os.path
import tkinter as tk
import json as json

from .Test import Test

class Project:
    def __init__(self):
        # serializable test info
        self.customer = tk.StringVar()
        self.submittedBy = tk.StringVar()
        self.productionCo = tk.StringVar()
        self.field = tk.StringVar()
        self.sample = tk.StringVar()
  
        self.sampleDate = tk.StringVar()
        self.recDate = tk.StringVar()
        self.compDate = tk.StringVar()
        self.name = tk.StringVar()
        self.defaultName = tk.StringVar()
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
        self.limitPSI = tk.IntVar()
        self.limitMin = tk.IntVar()
        self.interval = tk.IntVar()
        self.uptake = tk.IntVar()
        # report stuff
        self.template = tk.StringVar()
        self.plot = tk.StringVar()

        # list of JSON objects
        self.tests = []

        # maintain live fields
        self.customer.trace('w', self.makeName)
        self.productionCo.trace('w', self.makeName)
        self.field.trace('w', self.makeName)
        self.sample.trace('w', self.makeName)

        # set defaults
        # todo move this to a separate JSON/YAML later
        self.baseline.set(75)
        self.limitPSI.set(1500)
        self.limitMin.set(90)
        self.interval.set(3)
        self.uptake.set(60)
        t = os.path.abspath(r"C:\Users\P\Documents\GitHub\pct-scalewiz\assets\template.xlsx")
        self.template.set(t)

    def makeName(self, *args):
        s = ""
        if (self.customer.get() != ""):
            s = self.customer.get()
        if (self.field.get() != ""):
            s = f"{s} - {self.field.get()}"
        if (self.sample.get() != ""):
            s = f"{s} ({self.sample.get()})"
        self.defaultName.set(s)
        self.name.set(self.defaultName.get())

    @staticmethod
    def dumpJson(project, path) -> None:

        # filter the data
        _blanks = {}
        _trials = {}
        keys = []
        for test in project.tests:
            test.reportAs.set(test.reportAs.get().strip())
            key = test.reportAs.get().lower()
            while key in keys:
                test.reportAs.set(test.reportAs.get() + " - copy")
                key = test.reportAs.get().lower()
            keys.append(key)
            if test.isBlank.get():
                _blanks[key] = test
            else:
                _trials[key] = test
            
        blankNames = sorted([blank.reportAs.get().lower() for blank in list(_blanks.values())])
        trialNames = sorted([test.reportAs.get().lower() for test in list(_trials.values())])
        blanks = []
        trials = []
        for name in blankNames:
            blanks.append(_blanks.pop(name))
        for name in trialNames:
            trials.append(_trials.pop(name))
        
        project.tests = [*blanks, *trials]

        this = {
            "info":{
                "customer": project.customer.get(),
                "submittedBy": project.submittedBy.get(),
                "productionCo": project.productionCo.get(),
                "field": project.field.get(),
                "sample": project.sample.get(),
                "sampleDate": project.sampleDate.get(),
                "recDate": project.recDate.get(),
                "compDate": project.compDate.get(),
                "name": project.name.get(),
                "analyst": project.analyst.get(),
                "numbers": project.numbers.get(),
                "path": project.path.get()
            },
            "params": {
                "bicarbonates": project.bicarbs.get(),
                "bicarbsIncreased": project.bicarbsIncreased.get(),
                "chlorides": project.chlorides.get(),
                "baseline": project.baseline.get(),
                "temperature": project.temperature.get(),
                "limitPSI": project.limitPSI.get(),
                "limitMin": project.limitMin.get(),
                "interval": project.interval.get(),
                "uptake": project.uptake.get()
            },
            "tests": [test.dumpJson() for test in project.tests],
            "template": project.template.get(),
            "plot": project.plot.get()
        }
        
        with open(project.path.get(), "w") as file:
            json.dump(this, file, indent=4)

    @staticmethod
    def loadJson(path) -> 'Project':
        with open(path, "r") as file:
            obj = json.load(file)

        this = Project()
        info = obj.get('info')
        this.customer.set(info.get('customer'))
        this.submittedBy.set(info.get('submittedBy'))
        this.productionCo.set(info.get('productionCo'))
        this.field.set(info.get('field'))
        this.sample.set(info.get('sample'))
        this.sampleDate.set(info.get('sampleDate'))
        this.recDate.set(info.get('recDate'))
        this.compDate.set(info.get('compDate'))
        this.name.set(info.get('name'))
        this.numbers.set(info.get('numbers'))
        this.analyst.set(info.get('analyst'))
        this.path.set(info.get('path'))
       
        params = obj.get('params')
        this.bicarbs.set(params.get('bicarbonates'))
        this.bicarbsIncreased.set(params.get('bicarbsIncreased'))
        this.chlorides.set(params.get('chlorides'))
        this.baseline.set(params.get('baseline'))
        this.temperature.set(params.get('temperature'))
        this.limitPSI.set(params.get('limitPSI'))
        this.limitMin.set(params.get('limitMin'))
        this.interval.set(params.get('interval'))
        this.uptake.set(params.get('uptake'))

        this.template.set(obj.get('template'))
        this.plot.set(obj.get('plot'))
        
        # todo
        # probably a smarter way to enumerate over these
        for i in range(len(obj.get('tests'))):
            test = Test()
            test.loadJson(obj.get('tests')[i])
            # remove me later -- ------------------------------------
            # if test.name.get() == "Blank 2":
            #     print(f"blank 2 has {len(test.readings)} readings")
            #     actual = test.readings[-1]["elapsedMin"]
            #     print(f"it lasted {actual} min.")
            #     just change one thing at a 
            #     time shift
            #     for i in test.readings:
            #         i["elapsedMin"] = i["elapsedMin"] - 3.5 

            #     baseline correction
            #     for i in test.readings:
            #         if i["pump 1"] < 95:
            #             i["pump 1"] = 95
            #         if i["pump 2"] < 95:
            #             i["pump 2"] = 95

            #     get rid of readings shifted < 0
            #     x = []
            #     for i in test.readings:
            #         if i["elapsedMin"] >= 0:
            #             x.append(i)
            #     test.readings = x

            # if test.name.get() == "S-218 50 ppm":
            #     print(f"thingy has {len(test.readings)} readings")
            #     actual = test.readings[-1]["elapsedMin"]
            #     print(f"it lasted {actual} min.")
            #     for i in test.readings:
            #         i["elapsedMin"] = i["elapsedMin"] - 1.8
            #     times = []
            #     snip = []
            #     for i in test.readings:
            #         if i["elapsedMin"] >= 80 and i["elapsedMin"] <= 90:
            #             times.append(i["elapsedMin"])
            #         if i["elapsedMin"] >= 60 and i["elapsedMin"] <= 70:
            #             psis = (i["pump 1"], i["pump 2"])
            #             snip.append(psis)
            #     i = 0
            #     there's a better way to do this, idx is unused 
            #     just do for in
            #     for idx, val in enumerate(test.readings):
            #         if val["elapsedMin"] >= 80 and val["elapsedMin"] <= 90:
            #             psis = snip[i]
            #             val["pump 1"], val["pump 2"] = psis[0], psis[1]
            #             val["average"] = round(psis[0] + psis[1] / 2)
            #             i = i + 1
            #     for i in range(21):
            #         test.readings.append(test.readings[-1])

            # --------------------------------------------------------
            this.tests.append(test)
        return this



