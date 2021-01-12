"""Model object for a project. Provides a JSON/Tk mapping."""
import logging
import os.path
import tkinter as tk
import json as json

from .Test import Test

logger = logging.getLogger('scalewiz')

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
        t = os.path.abspath(r"assets/template.xlsx")
        self.template.set(t)

    def makeName(self, *args):

        # if self.productionCo.get() != "":
        #     initial = f"{self.editorProject.productionCo.get()} - {self.editorProject.field.get()} ({self.editorProject.sample.get()})"
        # else:
        #     initial = f"{self.editorProject.customer.get()} - {self.editorProject.field.get()} ({self.editorProject.sample.get()})"
        
        s = ""
        if self.productionCo.get() != "":
            s = self.productionCo.get().strip()
        else:
            s = self.customer.get().strip()
        if self.field.get() != "":
            s = f"{s} - {self.field.get()}".strip()
        if self.sample.get() != "":
            s = f"{s} ({self.sample.get()})".strip()
        # todo
        # we hold on to this -- no use for it yet !
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
        
        logger.info(f"Saved {project.name.get()} to {project.path.get()}")

    @staticmethod
    def loadJson(path) -> 'Project':
        logger.info(f"Loading from {path}")
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
         
            this.tests.append(test)
        return this



