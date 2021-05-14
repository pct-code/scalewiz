"""Handles a test."""

from __future__ import annotations

import logging
import os
import tkinter as tk
import typing
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from queue import Queue
from threading import Event
from time import monotonic, sleep, time
from tkinter import filedialog, messagebox

from py_hplc import NextGenPump

from scalewiz.components.test_handler_view import TestHandlerView
from scalewiz.models.project import Project
from scalewiz.models.test import Reading, Test

if typing.TYPE_CHECKING:
    from tkinter import ttk
    from typing import List


class TestHandler:
    """Handles a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name: str = "Nemo") -> None:
        self.name = name
        self.logger = logging.getLogger(f"scalewiz.{name}")
        self.view: TestHandlerView = None
        self.project = Project()
        self.test: Test = None
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.readings: Queue[dict] = Queue()
        self.editors: List[tk.Widget] = []  # list of views displaying the project
        self.max_readings: int = None  # max # of readings to collect
        self.max_psi_1: int = None
        self.max_psi_2: int = None
        self.log_handler: logging.FileHandler = None  # handles logging to log window
        # test handler view overwrites this attribute in the view's build()
        self.log_queue: Queue[str] = Queue()  # view pulls from this queue

        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stop_requested: Event = Event()
        self.progress = tk.IntVar()
        self.elapsed_min = tk.DoubleVar()  # used for evaluations

        self.pump1: NextGenPump = None
        self.pump2: NextGenPump = None

        # UI concerns
        self.is_running = tk.BooleanVar()
        self.is_done = tk.BooleanVar()
        self.new_test()

    def can_run(self) -> bool:
        """Returns a bool indicating whether or not the test can run."""
        return (
            (
                self.max_psi_1 <= self.project.limit_psi.get()
                or self.max_psi_2 <= self.project.limit_psi.get()
            )
            and self.elapsed_min.get() <= self.project.limit_minutes.get()
            and self.readings.qsize() < self.max_readings
            and not self.stop_requested.is_set()
        )

    def load_project(self, path: str = None, loaded: List[str] = []) -> None:
        """Opens a file dialog then loads the selected Project file."""
        # traces are set in Project and Test __init__ methods
        # we need to explicitly clean them up here
        if self.project is not None:
            for test in self.project.tests:
                test.remove_traces()
            self.project.remove_traces()

        if path is None:
            path = os.path.abspath(
                filedialog.askopenfilename(
                    initialdir='C:"',
                    title="Select project file:",
                    filetypes=[("JSON files", "*.json")],
                )
            )

        # check that the dialog succeeded, the file exists, and isn't already loaded
        if path != "" and os.path.isfile(path):
            if path in loaded:
                msg = "Attempted to load an already-loaded project"
                self.logger.warning(msg)
                messagebox.showwarning("Project already loaded", msg)
            else:
                self.project = Project()
                self.project.load_json(path)
                self.new_test()
                self.rebuild_views()
                self.logger.info("Loaded %s", self.project.name.get())

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""
        # todo disable the start button instead of this
        if self.is_running.get():
            return

        issues = []
        if not Path(self.project.path.get()).is_file:
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

        # this method will append issue msgs if any occur
        self.setup_pumps(issues)  # hooray for pointers
        if len(issues) > 0:
            messagebox.showwarning("Couldn't start the test", "\n".join(issues))
            for pump in (self.pump1, self.pump2):
                pump.close()
        else:
            self.stop_requested.clear()
            self.is_done.set(False)
            self.is_running.set(True)
            self.rebuild_views()
            self.update_log_handler()
            self.logger.info("submitting")
            self.pool.submit(self.take_readings)

    def take_readings(self) -> None:
        """Get ready to take readings, then start doing it on a second thread."""
        # run the uptake cycle ---------------------------------------------------------
        uptake = self.project.uptake_seconds.get()
        step = uptake / 100  # we will sleep for 100 steps
        self.pump1.run()
        self.pump2.run()
        rinse_start = monotonic()
        sleep(step)
        for i in range(100):
            if self.can_run():
                self.progress.set(i)
                sleep(step - ((monotonic() - rinse_start) % step))
            else:
                self.stop_test()
                break
        self.log_queue.put("")  # add newline for clarity
        # we use these in the loop
        interval = self.project.interval_seconds.get()
        test_start_time = monotonic()
        sleep(interval)
        # readings loop ----------------------------------------------------------------
        while self.can_run():
            minutes_elapsed = round((monotonic() - test_start_time) / 60, 2)

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
            self.logger.info(msg)

            self.readings.put(reading)
            self.elapsed_min.set(minutes_elapsed)
            prog = round((self.readings.qsize() / self.max_readings) * 100)
            self.logger.warning(
                "qsize is %s max is %s prog is %s",
                self.readings.qsize(),
                self.max_readings,
                prog,
            )
            self.progress.set(prog)

            if psi1 > self.max_psi_1:
                self.max_psi_1 = psi1
            if psi2 > self.max_psi_2:
                self.max_psi_2 = psi2

            # TYSM https://stackoverflow.com/a/25251804
            sleep(interval - ((monotonic() - test_start_time) % interval))
        # end of readings loop ---------------------------------------------------------
        self.stop_test()
        self.save_test()

    # because the readings loop is blocking, it is handled on a separate thread
    # beacuse of this, we have to interact with it in a somewhat backhanded way
    # this method is intended to be called from the test handler view
    def request_stop(self) -> None:
        """Requests that the Test stop."""
        if self.is_running.get():
            # the readings loop thread checks this flag on each iteration
            self.stop_requested.set()
            self.logger.info("Received a stop request")

    def stop_test(self) -> None:
        """Stops the pumps, closes their ports."""
        for pump in (self.pump1, self.pump2):
            if pump.is_open:
                pump.stop()
                pump.close()
                self.logger.info(
                    "Stopped and closed the device @ %s",
                    pump.serial.name,
                )

        self.is_done.set(True)
        self.logger.info("Test for %s has been stopped", self.test.name.get())

    def save_test(self) -> None:
        """Saves the test to the Project file in JSON format."""
        for reading in list(self.readings.queue):
            self.test.readings.append(reading)
        self.project.tests.append(self.test)
        self.project.dump_json()
        # refresh data / UI
        self.load_project(path=self.project.path.get())
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
            self.logger.info("set flowrate to %s", pump.flowrate)

    # logging stuff / methods that affect UI
    def new_test(self) -> None:
        """Initialize a new test."""
        self.logger.info("Initialized a new test")
        self.test = Test()
        with self.readings.mutex:
            self.readings.queue.clear()
        self.max_psi_1 = self.max_psi_2 = 0
        self.is_running.set(False)
        self.is_done.set(False)
        self.progress.set(0)
        self.logger.warning(
            "currently loaded %s with lim min",
            self.project.name.get(),
            self.project.limit_minutes.get(),
        )
        self.logger.warning(
            "lim_min is %s and interval is %s",
            self.project.limit_minutes.get(),
            self.project.interval_seconds.get(),
        )
        self.max_readings = round(
            self.project.limit_minutes.get() * 60 / self.project.interval_seconds.get()
        )
        self.logger.warning("max readings is %s", self.max_readings)

        self.rebuild_views()

    def rebuild_views(self) -> None:
        """Rebuild all open Widgets that could modify the Project file."""
        for widget in self.editors:
            if widget.winfo_exists():
                self.logger.debug("Rebuilding %s", widget)
                widget.build(reload=True)
            else:  # clean up as we go
                self.editors.remove(widget)
        if isinstance(self.view, TestHandlerView):
            self.view.build()
        self.logger.info("Rebuilt all view widgets")

    def update_log_handler(self) -> None:
        """Sets up the logging FileHandler to the passed path."""
        log_file = f"{round(time())}_{self.test.name.get()}_{date.today()}.txt"
        parent_dir = os.path.dirname(self.project.path.get())
        logs_dir = os.path.join(parent_dir, "logs")
        if not os.path.isdir(logs_dir):
            os.mkdir(logs_dir)
        log_path = os.path.join(logs_dir, log_file)

        if self.log_handler in self.logger.handlers:
            self.logger.removeHandler(self.log_handler)
        self.log_handler = logging.FileHandler(log_path)

        formatter = logging.Formatter(
            "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
        self.logger.info("Set up a log file at %s", log_file)
        self.logger.info("Starting a test for %s", self.project.name.get())

    def set_view(self, view: ttk.Frame) -> None:
        """Stores a ref to the view displaying the handler."""
        self.view = view
