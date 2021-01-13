"""Handles a test."""

# util
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import time
from datetime import date
import os
from serial import Serial, SerialException
from concurrent.futures import ThreadPoolExecutor

# internal
from ..components.ProjectEditor import ProjectEditor
from ..components.EvaluationWindow import EvaluationWindow
from ..models.Project import Project
from ..models.Test import Test
from ..models.TeledynePump import TeledynePump

logger = logging.getLogger('scalewiz')

class TestHandler():
    def __init__(self):
        # local state vars
        self.project = Project()
        self.test = Test()
        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stopRequested = False
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.queue = []
        self.progress = tk.IntVar()
        self.elapsed = tk.StringVar()

        self.editors = []

        # UI concerns
        self.isRunning = tk.BooleanVar()
        self.isDone = tk.BooleanVar()
        self.projBtnText = tk.StringVar()
        self.update_BtnText()

        # logging
        # todo add another logging handler here and set it to a file next to the project.json 

    def canRun(self) -> bool:
        value = (
            (self.maxPSI1 <= self.project.limitPSI.get() or self.maxPSI2 <= self.project.limitPSI.get())
            # todo stop doing this 
            and len(self.queue) < self.maxReadings()
            and not self.stopRequested
        )
        return value

    # todo should be using a tkVar+trace instead ... 
    def maxReadings(self) -> int:
        return round(self.project.limitMin.get() * 60 / self.project.interval.get()) + 1

    def loadProj(self, path = None):
        if path is None:
            path = filedialog.askopenfilename(
                initialdir="C:\"",
                title="Select project file:",
                filetypes=[("JSON files", "*.json")]
            )

        if not (path == ""):
            self.closeEditors()
            self.project = Project.loadJson(path)
            if path != self.project.path.get():
                logger.warning(f"{self.name} opened a Project whose actual path didn't match its path property")
                self.project.path.set(path)
                Project.dumpJson(self.project, path)
            self.update_BtnText()
            logger.info(f"Loaded {self.project.name.get()} to {self.name}")

    def startTest(self):
        if self.isRunning.get(): return

        if self.dev1.get() == "" or self.dev1.get() == "None found":
            msg = "Select a port for pump 1"
            messagebox.showwarning("Missing Device Port", msg)
            return

        if self.dev2.get() == "" or self.dev2.get() == "None found":
            msg = "Select a port for pump 1"
            messagebox.showwarning("Missing Device Port", msg)
            return

        if self.dev1.get() == self.dev2.get():
            msg = "Select two unique ports"
            messagebox.showwarning("Missing Device Port", msg)
            return

        if not os.path.isfile(self.project.path.get()):
            msg = "Select an existing project file first"
            messagebox.showwarning("Invalid Project Selected", msg)
            return
        
        if self.test.name.get() == "":
            msg = "Name the experiment before starting"
            messagebox.showwarning("Invalid Experiment Name", msg)
            return
        
        if self.test.clarity.get() == "":
            if self.test.isBlank.get():
                return
            msg = "Water clarity cannot be blank"
            messagebox.showwarning("Missing Water Clarity", msg)
            return

        self.setupPumps()

        if not self.pump1.port.isOpen():
            msg = f"Couldn't connect to {self.pump1.port.name}"
            messagebox.showwarning("Serial Exception", msg)
            return

        if not self.pump2.port.isOpen():
            msg = f"Couldn't connect to {self.pump2.port.name}"
            messagebox.showwarning("Serial Exception", msg)
            return

        # close any open editors
        self.closeEditors()
        self.stopRequested = False
        self.isDone.set(False)
        self.isRunning.set(True)
        self.progress.set(0)
        # make a new log file
        fileName = f"{self.test.name.get()} {date.today()}.txt"
        dirName = os.path.dirname(self.project.path.get())
        logFile = os.path.join(dirName, fileName)
        # update the file handler 
        if hasattr(self, 'logFileHandler'):
            logger.removeHandler(self.logFileHandler)
        self.logFileHandler = logging.FileHandler(logFile)
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.logFileHandler.setFormatter(formatter)
        self.logFileHandler.setLevel(logging.DEBUG)
        logger.addHandler(self.logFileHandler)
        logger.info(f"{self.name} set up a log file at {logFile}")
        logger.info(f"{self.name} is starting a test for {self.project.name.get()}")
        self.pool.submit(self.takeReadings)
    
    def takeReadings(self):
        # set default values for this instance of the test loop
        self.queue = []
        self.maxPSI1 = self.maxPSI2 = 0
        # start the pumps
        self.pump1.run()
        self.pump2.run()
        uptake = self.project.uptake.get()
        for i in range(uptake):
            self.toLog(f"Awaiting uptake time {uptake - i} s ...")
            time.sleep(1)
        self.toLog("")
        interval = self.project.interval.get()
        snooze = round(interval * 0.9, 2)
        # assigning these vars isnt just to make them shorter
        # since we don't expect the values to change referencing them this way
        # is slightly less expensive than requesting the value from its tkVar on each iteration
        # startTime = time.time()
        # set this here so we can take a reading on the firt iteration
        # not anymore ? emulating do while
        # see indent on snooze call at end of while loop
        startTime = time.time()
        readingStart = startTime - interval

        # readings loop -------------------------------------------------------
        while(self.canRun()):
            if time.time() - readingStart >= interval:
                readingStart = time.time()
                elapsedMin = round((time.time() - startTime)/60, 2)
                # changed elapsed min to 
                # todo add ++ here???
                # elapsedMin = round(len(self.queue) * interval / 60, 2)

                psi1 = self.pump1.pressure()
                psi2 = self.pump2.pressure()
                collected = time.time() - readingStart
                logger.debug(f"{self.name} collected both PSIs in {collected} s")
                average = round(((psi1 + psi2)/2))

                # todo
                # if psi1 > limitPSI: psi1 = limitPSI
                # if psi2 > limitPSI: psi2 = limitPSI
                reading = {
                    "elapsedMin": elapsedMin,
                    "pump 1": psi1,
                    "pump 2": psi2,
                    "average": average
                }

                # make a message for the log in the test handler view
                msg = f"@ {elapsedMin:.2f} min; pump1: {psi1}, pump2: {psi2}, avg: {average}"
                self.toLog(msg)
                logger.info(f"{self.name} - {msg}")

                # why do this vs adding to test directly?
                # -> trying to not access same obj across threads
                self.queue.append(reading)

                self.elapsed.set(f"{elapsedMin:.2f} min.")
                self.progress.set(round(len(self.queue) / self.maxReadings() * 100))

                if psi1 > self.maxPSI1: self.maxPSI1 = psi1
                if psi2 > self.maxPSI2: self.maxPSI2 = psi2
                logger.debug(f"Finished doing everything else in {time.time() - readingStart - collected} s")
                logger.debug(f"{self.name} collected data in {time.time() - readingStart}")
                time.sleep(snooze)
        # end of readings loop ------------------------------------------------
        
        # find the actual elapsed time
        trueElapsed = round((time.time() - startTime) / 60, 2)
        # compare to the most recent elapsedMin value
        if trueElapsed != elapsedMin:
            # maybe make a dialog pop up instead?
            self.toLog(f"The test says it took {elapsedMin} min.")
            self.toLog(f"but really it took {trueElapsed} min. (I counted)")
            logger.warning(f"{self.name} - {elapsedMin} was really {trueElapsed} ({len(self.queue)}/{self.maxReadings()})")

        self.stopTest()
        self.saveTestToProject()

    # because the readings loop is blocking, it is handled on a separate thread
    # beacuse of this, we have to interact with it in a somewhat backhanded way
    # this method is intended to be called from the test handler view module on a UI button click
    def requestStop(self):
        if not self.isRunning.get(): return 

        if self.isRunning.get():
            # the readings loop thread checks this flag on each iteration
            self.stopRequested = True
            logger.info(f"{self.name} received a stop request")

    def stopTest(self):
        if self.pump1.port.isOpen():
            self.pump1.stop()
            self.pump1.close()
            logger.info(f"{self.name} has stopped and closed the device @ {self.pump1.port.port}")
        
        if self.pump2.port.isOpen():
            self.pump2.stop()
            self.pump2.close()
            logger.info(f"{self.name} has stopped and closed the device @ {self.pump1.port.port}")

        self.isDone.set(True)
        self.progress.set(0)
        self.elapsed.set("")
        logger.info(f"{self.name}'s test has been stopped")

    def saveTestToProject(self):
        for reading in self.queue:
            self.test.readings.append(reading)
        self.queue.clear()
        self.project.tests.append(self.test)
        Project.dumpJson(self.project, self.project.path.get())
        logger.info(f"{self.name} saved {self.project.name.get()} to {self.project.path.get()}")
        self.loadProj(path=self.project.path.get())

    def setupPumps(self):
        # the timeout values are an alternative to using TextIOWrapper
        # the values chosen were suggested by the pump's documentation
        try:
            port1 = Serial(self.dev1.get(), timeout=0.05)
            self.pump1 = TeledynePump(port1)
            logger.info(f"{self.name} established a connection to {port1.port}")
            
            port2 = Serial(self.dev2.get(), timeout=0.05)
            self.pump2 = TeledynePump(port2)
            logger.info(f"{self.name} established a connection to {port2.port}")
        except SerialException as e:
            logger.exception(e)
            messagebox.showwarning("Serial Exception", e)

    # methods that affect UI

    def newTest(self):
        logger.info(f"{self.name} initialized a new test")
        self.test = Test()
        self.isRunning.set(False)
        self.isDone.set(False)
        self.elapsed.set("")
        # todo why is this here?
        self.parent.pltFrm.destroy()
        self.parent.logFrm.destroy()
        self.parent.build()
  
    def modProj(self):
        if len(self.editors) > 0: 
            messagebox.showwarning("Project is locked", "Can't modify a Project while it is being accessed")
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", self.closeEditors)
        window.resizable(0, 0)
        self.editors.append(window)
        editor = ProjectEditor(window, self)
        editor.grid()
        logger.info(f"{self.name} opened an editor window for {self.project.name.get()}")

    def evalProj(self):
        if len(self.editors) > 0: 
            messagebox.showwarning("Project is locked", "Can't modify a Project while it is being accessed")
            return
        window = tk.Toplevel()
        window.protocol("WM_DELETE_WINDOW", self.closeEditors)
        window.resizable(0, 0)
        self.editors.append(window)
        editor = EvaluationWindow(window, self)
        editor.grid()
        logger.info(f"{self.name} opened an evaluation window for {self.project.name.get()}")

    # todo is this necessary??
    def update_BtnText(self):
            if(self.project.name.get() == ""):
                self.projBtnText.set("Select a project")
            else:
                self.projBtnText.set(self.project.name.get())

    # todo give this a better name 
    def closeEditors(self):
        for window in self.editors:
            self.editors.remove(window)
            window.destroy()
        logger.info(f"{self.name} has closed all editor windows")
  
    def toLog(self, msg):
        self.logText.configure(state='normal')
        self.logText.insert('end', msg + "\n")
        self.logText.configure(state='disabled')
        self.logText.see('end')