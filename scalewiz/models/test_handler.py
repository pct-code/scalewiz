"""Handles a test."""

from __future__ import annotations

import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from logging import DEBUG, FileHandler, Formatter, getLogger
from pathlib import Path
from queue import Queue
from threading import Event
from time import monotonic, time
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

from py_hplc import NextGenPump

import scalewiz
from scalewiz.models.project import Project
from scalewiz.models.test import Reading, Test

if TYPE_CHECKING:
    from logging import Logger
    from typing import List, Set


class TestHandler:
    """Handles a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name: str = "Nemo") -> None:
        self.name = name
        self.root: tk.Tk = scalewiz.ROOT
        self.logger: Logger = getLogger(f"scalewiz.{name}")
        self.project: Project = Project()
        self.test: Test = None
        self.readings: Queue[Reading] = Queue()
        self.max_readings: int = None  # max # of readings to collect
        self.max_psi_1: int = None
        self.max_psi_2: int = None
        self.log_handler: FileHandler = None  # handles logging to log window
        # test handler view overwrites this attribute in the view's build()
        self.log_queue: Queue[str] = Queue()  # view pulls from this queue
        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stop_requested: Event = Event()
        self.progress = tk.IntVar()
        self.elapsed_min: float = float()  # used for evaluations
        self.pump1: NextGenPump = None
        self.pump2: NextGenPump = None
        self.pool = ThreadPoolExecutor(max_workers=1)

        # UI concerns
        self.views: List[tk.Widget] = []  # list of views displaying the project
        self.is_running: bool = bool()
        self.is_done: bool = bool()
        self.new_test()

    @property
    def can_run(self) -> bool:
        """Returns a bool indicating whether or not the test can run."""
        return (
            (
                self.max_psi_1 < self.project.limit_psi.get()
                or self.max_psi_2 < self.project.limit_psi.get()
            )
            and self.elapsed_min < self.project.limit_minutes.get()
            and self.readings.qsize() < self.max_readings
            and not self.stop_requested.is_set()
        )

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""
        issues = []
        if not Path(self.project.path.get()).is_file():
            msg = "Select an existing project file first"
            issues.append(msg)

        if self.test.name.get() == "":
            msg = "Name the experiment before starting"
            issues.append(msg)

        if self.test.name.get() in {test.name.get() for test in self.project.tests}:
            msg = "A test with this name already exists in the project"
            issues.append(msg)

        if self.test.clarity.get() == "" and not self.test.is_blank.get():
            msg = "Water clarity cannot be blank"
            issues.append(msg)

        self.update_log_handler(issues)

        # this method will append issue msgs if any occur
        self.setup_pumps(issues)  # hooray for pointers
        if len(issues) > 0:
            messagebox.showwarning("Couldn't start the test", "\n".join(issues))
            for pump in (self.pump1, self.pump2):
                pump.close()
        else:
            self.stop_requested.clear()
            self.is_done = False
            self.is_running = True
            self.rebuild_views()
            self.uptake_cycle()

    def uptake_cycle(self) -> None:
        """Get ready to take readings."""
        # run the uptake cycle ---------------------------------------------------------
        uptake = self.project.uptake_seconds.get() * 1000  # ms
        ms_step = round((uptake / 100))  # we will sleep for 100 steps
        self.pump1.run()
        self.pump2.run()

        def cycle(start, i, step) -> None:
            if self.can_run:
                if i < 100:
                    i += 1
                    self.progress.set(i)
                    self.root.after(
                        round(step - ((monotonic() - start) % step)),
                        cycle,
                        start,
                        i,
                        step,
                    )
                else:
                    self.take_readings()
            else:
                self.stop_test(save=False)

        cycle(monotonic(), 0, ms_step)

    def take_readings(self, start_time: float = None, interval: float = None) -> None:
        if start_time is None:
            start_time = monotonic()
        if interval is None:
            interval = self.project.interval_seconds.get() * 1000
        # readings loop ----------------------------------------------------------------
        if self.can_run:
            minutes_elapsed = round((monotonic() - start_time) / 60, 2)

            psi1 = self.pump1.pressure
            psi2 = self.pump2.pressure
            average = round(((psi1 + psi2) / 2))

            reading = Reading(
                elapsedMin=minutes_elapsed, pump1=psi1, pump2=psi2, average=average
            )

            # make a message for the log in the test handler view
            msg = "@ {:.2f} min; pump1: {}, pump2: {}, avg: {}".format(
                minutes_elapsed, psi1, psi2, average
            )
            self.log_queue.put(msg)
            self.logger.debug(msg)

            self.readings.put(reading)
            self.elapsed_min = minutes_elapsed
            prog = round((self.readings.qsize() / self.max_readings) * 100)
            self.progress.set(prog)

            if psi1 > self.max_psi_1:
                self.max_psi_1 = psi1
            if psi2 > self.max_psi_2:
                self.max_psi_2 = psi2

            # TYSM https://stackoverflow.com/a/25251804
            self.root.after(
                round(interval - ((monotonic() - start_time) % interval)),
                self.take_readings,
                start_time,
                interval,
            )
        else:
            # end of readings loop -----------------------------------------------------
            self.logger.warn("about to request saving")
            self.stop_test(save=True)

    # logging stuff / methods that affect UI
    def new_test(self) -> None:
        """Initialize a new test."""
        self.logger.info("Initializing a new test")
        if isinstance(self.test, Test):
            self.test.remove_traces()
            del self.test
        self.test = Test()
        with self.readings.mutex:
            self.readings.queue.clear()
        self.max_psi_1, self.max_psi_2 = 0, 0
        self.is_running, self.is_done = False, False
        self.progress.set(0)
        self.max_readings = round(
            self.project.limit_minutes.get() * 60 / self.project.interval_seconds.get()
        )
        self.rebuild_views()

    def setup_pumps(self, issues: List[str] = None) -> None:
        """Set up the pumps with some default values.
        Appends errors to the passed list
        """
        if issues is None:
            issues = []

        if self.dev1.get() in ("", "None found"):
            issues.append("Select a port for pump 1")

        if self.dev2.get() in ("", "None found"):
            issues.append("Select a port for pump 2")

        if self.dev1.get() == self.dev2.get():
            issues.append("Select two unique ports")
        else:
            self.pump1 = NextGenPump(self.dev1.get(), self.logger)
            self.pump2 = NextGenPump(self.dev2.get(), self.logger)

        for pump in (self.pump1, self.pump2):
            if pump is None or not pump.is_open:
                issues.append(f"Couldn't connect to {pump.serial.name}")
                continue
            pump.flowrate = self.project.flowrate.get()
            self.logger.info("Set flowrates to %s", pump.flowrate)

    def request_stop(self) -> None:
        """Requests that the Test stop."""
        # because the readings loop is blocking, it is handled on a separate thread
        # beacuse of this, we have to interact with it in a somewhat backhanded way
        # this method is intended to be called from the test handler view
        if self.is_running:
            # the readings loop thread checks this flag on each iteration
            self.stop_requested.set()
            self.logger.info("Received a stop request")

    def stop_test(self, save: bool = True) -> None:
        """Stops the pumps, closes their ports."""
        for pump in (self.pump1, self.pump2):
            if pump.is_open:
                pump.stop()
                pump.close()
                self.logger.info(
                    "Stopped and closed the device @ %s",
                    pump.serial.name,
                )

        self.is_done = True
        self.is_running = False
        self.logger.warn("Test for %s has been stopped", self.test.name.get())
        for _ in range(3):
            self.views[0].bell()
        if save:
            self.logger.warn("TRYING TO SAVE")
            self.save_test()
        self.rebuild_views()

    def save_test(self) -> None:
        """Saves the test to the Project file in JSON format."""
        self.logger.warn("TRYING TO SAVE")
        for reading in tuple(self.readings.queue):
            self.test.readings.append(reading)
        self.logger.warn(
            "saved %s readings to %s", len(self.test.readings), self.test.name.get()
        )
        self.project.tests.append(self.test)
        try:
            self.project.dump_json()
        except Exception as err:
            self.logger.exception(err)

        # refresh data / UI
        self.load_project(path=self.project.path.get(), new_test=False)
        # self.rebuild_views()

    def rebuild_views(self) -> None:
        """Rebuild all open Widgets that display or modify the Project file."""
        for widget in self.views:
            if widget.winfo_exists():
                self.logger.debug("Rebuilding %s", widget)
                self.root.after(0, lambda: widget.build(reload=True))
            else:  # clean up as we go
                self.views.remove(widget)

        self.logger.info("Rebuilt all view widgets")

    def update_log_handler(self, issues: List[str]) -> None:
        """Sets up the logging FileHandler to the passed path."""
        try:
            id = "".join(char for char in self.test.name.get() if char.isalnum())
            log_file = f"{time():.0f}_{id}_{date.today()}.txt"
            parent_dir = Path(self.project.path.get()).parent.resolve()
            logs_dir = parent_dir.joinpath("logs").resolve()
            if not logs_dir.is_dir():
                logs_dir.mkdir()
            log_path = Path(logs_dir).joinpath(log_file).resolve()
            self.log_handler = FileHandler(log_path)
        except Exception as err:  # bad path chars from user can bug here
            issues.append("Bad log file")
            issues.append(str(err))
            return
        else:
            formatter = Formatter(
                "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            if self.log_handler in self.logger.handlers:  # remove the old one
                self.logger.removeHandler(self.log_handler)
            self.log_handler.setFormatter(formatter)
            self.log_handler.setLevel(DEBUG)
            self.logger.addHandler(self.log_handler)
            self.logger.info("Set up a log file at %s", log_file)
            self.logger.info("Starting a test for %s", self.project.name.get())

    def load_project(
        self, path: str = None, loaded: Set[Path] = [], new_test: bool = True
    ) -> None:
        """Opens a file dialog then loads the selected Project file.

        `loaded` gets built from scratch every time it is passed in -- no need to update
        """
        if path is None:
            path = filedialog.askopenfilename(
                initialdir='C:"',
                title="Select project file:",
                filetypes=[("JSON files", "*.json")],
            )
        if path is not None:
            path = Path(path).resolve()

        # check that the dialog succeeded, the file exists, and isn't already loaded
        if path.is_file():
            if path in loaded:
                msg = "Attempted to load an already-loaded project"
                self.logger.warning(msg)
                messagebox.showwarning("Project already loaded", msg)
            else:
                # traces are set in Project and Test __init__ methods
                # we need to explicitly clean them up here
                self.project.remove_traces()
                del self.project
                self.project = Project()
                self.project.load_json(path)
                if new_test:
                    self.new_test()
                self.logger.info("Loaded %s", self.project.name.get())
