"""A Tkinter widget for handling tests."""

import logging
import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk

import matplotlib.pyplot as plt
import serial.tools.list_ports as list_ports

from components.LivePlot import LivePlot

logger = logging.getLogger("scalewiz")

# todo #1 these frames should probably be separated into separate classes


class TestHandlerView(ttk.Frame):
    def __init__(self, parent, handler):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.handler = handler
        self.handler.parent = self
        self.devList = []
        self.build()

    def setBindings(self):
        self.handler.test.isBlank.trace(
            "w", self.update_TestType
        )  # might have to retrace on new test
        self.handler.isRunning.trace("w", self.update_InputFrame)
        self.handler.isDone.trace("w", self.update_InitBtn)
        self.handler.dev1.trace("w", self.update_DevList)
        self.handler.dev2.trace("w", self.update_DevList)

    def build(self):
        for child in self.winfo_children():
            child.destroy()

        self.setBindings()
        self.inputs = []
        self.iFrm = ttk.Frame(self)
        self.iFrm.grid(row=0, column=0, sticky="new")
        # row 0 ---------------------------------------------------------------
        devLbl = ttk.Label(self.iFrm, text="      Devices:")
        devLbl.bind("<Button-1>", lambda _: self.update_DevList())

        # put the boxes in a frame to make life easier
        frame = ttk.Frame(self.iFrm)  # this frame will set the width for the col
        self.dev1Ent = ttk.Combobox(
            frame, width=15, textvariable=self.handler.dev1, values=self.devList
        )
        self.dev2Ent = ttk.Combobox(
            frame, width=15, textvariable=self.handler.dev2, values=self.devList
        )
        self.dev1Ent.grid(row=0, column=0, sticky=tk.W)
        self.dev2Ent.grid(row=0, column=1, sticky=tk.E, padx=(4, 0))
        self.inputs.append(self.dev1Ent)
        self.inputs.append(self.dev2Ent)
        self.render(devLbl, frame, 0)

        # row 1 ---------------------------------------------------------------
        projLbl = ttk.Label(self.iFrm, text="Project:")
        projBtn = ttk.Label(
            self.iFrm, textvariable=self.handler.project.name, anchor="center"
        )
        self.inputs.append(projBtn)
        self.render(projLbl, projBtn, 1)

        # row 2 ---------------------------------------------------------------
        typeLbl = ttk.Label(self.iFrm, text="Test Type:")
        entFrm = ttk.Frame(self.iFrm)
        entFrm.grid_columnconfigure(0, weight=1)
        entFrm.grid_columnconfigure(1, weight=1)
        foo = self.handler.test.isBlank
        blankRadio = ttk.Radiobutton(entFrm, text="Blank", variable=foo, value=True)
        blankRadio.grid(row=0, column=0)
        trialRadio = ttk.Radiobutton(entFrm, text="Trial", variable=foo, value=False)
        trialRadio.grid(row=0, column=1)
        self.inputs.append(blankRadio)
        self.inputs.append(trialRadio)
        self.render(typeLbl, entFrm, 2)

        # row 3 ---------------------------------------------------------------
        self.grid_rowconfigure(3, weight=1)
        # row 3a ---------------------------------------------------------------
        self.trialLblFrm = ttk.Frame(self.iFrm)
        ttk.Label(self.trialLblFrm, text="Chemical:").grid(
            row=0, column=0, sticky=tk.E, pady=1
        )
        ttk.Label(self.trialLblFrm, text="Rate (ppm):").grid(
            row=1, column=0, sticky=tk.E, pady=1
        )
        ttk.Label(self.trialLblFrm, text="Clarity:").grid(
            row=2, column=0, sticky=tk.E, pady=1
        )

        self.trialEntFrm = ttk.Frame(self.iFrm)
        self.trialEntFrm.grid_columnconfigure(0, weight=1)
        chemEnt = ttk.Entry(self.trialEntFrm, textvariable=self.handler.test.chemical)
        chemEnt.grid(row=0, column=0, sticky="ew", pady=1)
        rateEnt = ttk.Spinbox(
            self.trialEntFrm, textvariable=self.handler.test.rate, from_=0, to=999999
        )
        rateEnt.grid(row=1, column=0, sticky="ew", pady=1)
        clarity_options = ["Clear", "Slightly hazy", "Hazy"]
        clarityEnt = ttk.Combobox(
            self.trialEntFrm,
            values=clarity_options,
            textvariable=self.handler.test.clarity,
        )
        clarityEnt.grid(row=2, column=0, sticky="ew", pady=1)
        clarityEnt.current(0)

        self.inputs.append(chemEnt)
        self.inputs.append(rateEnt)
        self.inputs.append(clarityEnt)

        # row 3b ---------------------------------------------------------------
        self.blankLbl = ttk.Label(self.iFrm, text="Name:")
        self.blankEnt = ttk.Entry(self.iFrm, textvariable=self.handler.test.name)
        self.inputs.append(self.blankEnt)

        # row 4 ---------------------------------------------------------------
        notesLbl = ttk.Label(self.iFrm, text="Notes:")
        notesEnt = ttk.Entry(self.iFrm, textvariable=self.handler.test.notes)
        self.inputs.append(notesEnt)
        self.render(notesLbl, notesEnt, 4)

        # iFrm end ------------------------------------------------------------

        # row 1 ---------------------------------------------------------------
        frame = ttk.Frame(self)
        self.startBtn = ttk.Button(
            frame, text="Start", command=lambda: self.handler.startTest()
        )
        stopBtn = ttk.Button(
            frame, text="Stop", command=lambda: self.handler.requestStop()
        )
        plotBtn = ttk.Button(
            frame, text="Toggle Details", command=lambda: self.update_PlotVisible()
        )

        self.startBtn.grid(row=0, column=0)
        stopBtn.grid(row=0, column=1)
        plotBtn.grid(row=0, column=2)

        progressBar = ttk.Progressbar(frame, variable=self.handler.progress)
        progressBar.grid(row=1, columnspan=3, sticky="new")
        self.elapsed = ttk.Label(frame, textvariable=self.handler.elapsed)
        self.elapsed.grid(row=1, column=1)
        frame.grid(row=1, column=0, padx=1, pady=1, sticky="n")
        self.initBtn = ttk.Button(
            frame, text="New", command=lambda: self.handler.newTest()
        )

        # rows 0-1 -------------------------------------------------------------
        # close all pyplots to prevent memory leak
        plt.close("all")
        self.pltFrm = LivePlot(self, self.handler)
        self.grid_columnconfigure(1, weight=1)  # let it grow
        self.grid_rowconfigure(1, weight=1)

        # row 2 ---------------------------------------------------------------
        self.logFrm = ttk.Frame(self)
        self.logText = tk.scrolledtext.ScrolledText(
            self.logFrm, background="white", height=5, width=44, state="disabled"
        )
        # todo alert alert this is not elegant
        self.handler.logText = self.logText  # this is bad ?
        self.logText.grid(sticky="ew")

        self.update_TestType()
        self.update_InitBtn()
        self.update_DevList()

    # methods to update local state

    def render(self, label, entry, row):
        label.grid(row=row, column=0, sticky=tk.N + tk.E)
        entry.grid(row=row, column=1, sticky=tk.N + tk.E + tk.W, pady=1, padx=1)

    # todo shouldn't this be held by the test handler?
    def update_DevList(self, *args):
        old = [i for i in self.devList]
        self.devList = sorted([i.device for i in list_ports.comports()])
        if len(self.devList) < 1:
            self.devList.append("None found")
        self.dev1Ent.configure(values=self.devList)
        self.dev2Ent.configure(values=self.devList)
        for i in self.devList:
            if not i in old and not i == "None found":
                logger.info(f"{self.handler.name} found device: {i}")

    def update_InputFrame(self, *args):
        for child in self.inputs:
            if self.handler.isRunning.get():
                child.configure(state="disabled")
            else:
                child.configure(state="normal")

    def update_InitBtn(self, *args):
        if self.handler.isDone.get():
            self.startBtn.grid_remove()
            self.initBtn.grid(row=0, column=0)
        else:
            self.initBtn.grid_remove()
            self.startBtn.grid(row=0, column=0)

    def update_TestType(self, *args):
        if self.handler.test.isBlank.get():
            self.trialLblFrm.grid_remove()
            self.trialEntFrm.grid_remove()
            self.render(self.blankLbl, self.blankEnt, 3)
            logger.info(f"{self.handler.name}: changed to Blank mode")
        else:
            self.blankLbl.grid_remove()
            self.blankEnt.grid_remove()
            self.render(self.trialLblFrm, self.trialEntFrm, 3)
            logger.info(f"{self.handler.name}: changed to Trial mode")

    def update_PlotVisible(self):
        isVisible = bool()
        # check if the plot is gridded
        if not self.pltFrm.grid_info() == {}:
            isVisible = True

        for tab in self.parent.tabs():
            this = self.parent.nametowidget(tab)
            if not isVisible:
                logger.info(f"{this.handler.name}: Showing details view")
                this.pltFrm.grid(row=0, column=1, rowspan=3)
                this.logFrm.grid(row=2, column=0, sticky="ew")
            else:
                logger.info(f"{this.handler.name}: Hiding details view")
                this.pltFrm.grid_remove()
                this.logFrm.grid_remove()
