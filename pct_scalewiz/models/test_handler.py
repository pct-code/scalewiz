"""Handles a test."""

from __future__ import annotations

import logging
import os
from time import monotonic, sleep, time
import tkinter as tk
import typing
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from queue import Queue
from datetime import date
from tkinter import filedialog, messagebox

from py_hplc import NextGenPump

from pct_scalewiz.models.project import Project
from pct_scalewiz.models.test import Test

if typing.TYPE_CHECKING:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
    from typing import List

    from pct_scalewiz.components.test_handler_view import TestHandlerView

logger = logging.getLogger("scalewiz")


class TestHandler:
    """Handles a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name: str = "Nemo") -> None:
        self.name = name
        self.view: TestHandlerView = None
        self.project = Project()
        self.test: Test = None
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.readings: Queue[dict] = Queue()
        self.editors: list[tk.Toplevel] = []  # list of views displaying the project
        self.max_readings: int = None  # max # of readings to collect
        self.max_psi_1: int = None
        self.max_psi_2: int = None
        self.log_handler: logging.FileHandler = None

        # test handler view overwrites this attribute in the view's build()
        self.log_text: ScrolledText = None

        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stop_requested: Event = Event()
        self.progress = tk.IntVar()
        self.elapsed = tk.StringVar()

        self.pump1: NextGenPump = None
        self.pump2: NextGenPump = None

        # UI concerns
        self.is_running = tk.BooleanVar()
        self.is_done = tk.BooleanVar()
        self.new_test()

    def get_can_run(self) -> bool:
        """Returns a bool indicating whether or not the test can run."""
        return (
            (
                self.max_psi_1 <= self.project.limit_psi.get()
                or self.max_psi_2 <= self.project.limit_psi.get()
            )
            and len(self.readings) < self.max_readings
            and not self.stop_requested.is_set()
        )

    def load_project(self, path: str = None) -> None:
        """Opens a file dialog then loads the selected Project file."""
        # traces are set in Project and Test __init__s
        # we need to explicitly clean them up here
        if self.project is not None:
            for test in self.project.tests:
                test.remove_traces()
            self.project.remove_traces()

        if path is None:
            path = filedialog.askopenfilename(
                initialdir='C:"',
                title="Select project file:",
                filetypes=[("JSON files", "*.json")],
            )

        if path != "" and os.path.isfile(path):
            self.project = Project()
            self.project.load_json(path)
            self.rebuild_editors()
            logger.info("Loaded %s to %s", self.project.name.get(), self.name)

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""
        # todo disable the start button instead of this
        if self.is_running.get():
            return

        issues = []
        if not os.path.exists(self.project.path.get()):
            msg = "Select an existing project file first"
            issues.append(msg)

        if self.test.name.get() == "":
            msg = "Name the experiment before starting"
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

        self.stop_requested.clear()
        self.is_done.set(False)
        self.is_running.set(True)
        self.update_log_handler()
        self.pool.submit(self.take_readings, self.stop_requested)

    

    def take_readings(self, event: Event) -> None:
        """Get ready to take readings, then start doing it on a second thread."""
        # set default values for this instance of the test loop
        self.readings.clear()
        self.max_psi_1 = self.max_psi_2 = 0
        # start the pumps
        self.pump1.run()
        self.pump2.run()
        # run the uptake cycle
        uptake = self.project.uptake.get()
        for i in range(uptake):
            if self.get_can_run():
                self.elapsed.set(f"{uptake - i} s")
                self.progress.set(round(i / uptake * 100))
                sleep(1)
            else:
                self.stop_test()
                break

        self.to_log("")
        interval = self.project.interval.get()
        
        test_start_time = monotonic()
        reading_start = test_start_time - interval
        # readings loop ----------------------------------------------------------------
        while self.get_can_run():
            minutes_elapsed = round((monotonic() - test_start_time) / 60, 2)

            psi1 = self.pump1.pressure
            psi2 = self.pump2.pressure
            average = round(((psi1 + psi2) / 2))
            reading = {
                "elapsedMin": minutes_elapsed,
                "pump 1": psi1,
                "pump 2": psi2,
                "average": average,
            }

            # make a message for the log in the test handler view
            msg = "@ {} min; pump1: {}, pump2: {}, avg: {}".format(
                minutes_elapsed, psi1, psi2, average
            )
            self.to_log(msg)
            logger.info("%s - %s", self.name, msg)

            self.readings.append(reading)

            self.elapsed.set(f"{minutes_elapsed} min.")
            self.progress.set(round(len(self.readings) / self.max_readings * 100))

            if psi1 > self.max_psi_1:
                self.max_psi_1 = psi1
            if psi2 > self.max_psi_2:
                self.max_psi_2 = psi2

            event.wait(interval - ((monotonic() - test_start_time) % interval))
        # end of readings loop ---------------------------------------------------------

        # find the actual elapsed time
        actual_elapsed = round((monotonic() - test_start_time) / 60, 2)
        # compare to the most recent minutes_elapsed value
        if actual_elapsed != minutes_elapsed:
            # maybe make a dialog pop up instead?
            self.to_log(f"The test says it took {minutes_elapsed} min.")
            self.to_log(f"but really it took {actual_elapsed} min. (I counted)")
            logger.warning(
                "%s - %s was really %s (%s)",
                self.name,
                minutes_elapsed,
                actual_elapsed,
                len(self.readings) / self.max_readings,
            )

        self.stop_test()
        self.save_test()

    # because the readings loop is blocking, it is handled on a separate thread
    # beacuse of this, we have to interact with it in a somewhat backhanded way
    # this method is intended to be called from the test handler view
    def request_stop(self) -> None:
        """Requests that the Test stop."""
        if self.is_running.get():
            # the readings loop thread checks this flag on each iteration
            self.stop_requested = True
            logger.info("%s: Received a stop request", self.name)

    def stop_test(self) -> None:
        """Stops the pumps, closes their ports."""
        for pump in (self.pump1, self.pump2):
            if pump.is_open:
                pump.stop()
                pump.close()
                logger.info(
                    "%s: Stopped and closed the device @ %s",
                    self.name,
                    pump.serial.name,
                )

        self.is_done.set(True)
        logger.info("%s: Test for %s has been stopped", self.name, self.test.name.get())

    def save_test(self) -> None:
        """Saves the test to the Project file in JSON format."""
        for reading in self.readings:
            self.test.readings.append(reading)
        self.project.tests.append(self.test)
        self.project.dump_json()
        self.load_project(path=self.project.path.get())
        self.rebuild_editors()

    def setup_pumps(self, issues: List[str] = None) -> None:
        """Set up the pumps with some default values.
        Appends errors to the passed list
        """
        if issues is None:
            issues = []

        if self.dev1.get() in ("", "None found"):
            msg = "Select a port for pump 1"
            issues.append(msg)

        if self.dev2.get() in ("", "None found"):
            msg = "Select a port for pump 2"
            issues.append(msg)

        if self.dev1.get() == self.dev2.get():
            msg = "Select two unique ports"
            issues.append(msg)
        else:
            self.pump1 = NextGenPump(self.dev1.get(), logger)
            self.pump2 = NextGenPump(self.dev2.get(), logger)

        for pump in (self.pump1, self.pump2):
            if pump is None or not pump.is_open:
                issues.append(f"Couldn't connect to {pump.serial.name}")


    # logging stuff / methods that affect UI
    def new_test(self) -> None:
        """Initialize a new test."""
        logger.info("%s: Initialized a new test", self.name)
        self.test = Test()
        self.readings.clear()
        self.is_running.set(False)
        self.is_done.set(False)
        self.progress.set(0)
        self.elapsed.set("")
        self.max_readings = (
            round(self.project.limit_minutes.get() * 60 / self.project.interval.get())
            + 1
        )
        # rebuild the TestHandlerView
        if self.view is not None:
            self.view.build()

    def rebuild_editors(self) -> None:
        """Rebuild all open Toplevels that could overwrite the Project file."""
        for window in self.editors:
            if window.winfo_exists() == 1:
                logger.debug("rebuilding %s", window)
                window.build(reload=True)
        logger.info("%s has rebuilt all editor windows", self.name)

    def update_log_handler(self) -> None:
        """Sets up the logging FileHandler to the passed path."""
        log_file = f"{round(time())}_{self.test.name.get()}_{date.today()}.txt"
        parent_dir = os.path.dirname(self.project.path.get())
        logs_dir = os.path.join(parent_dir, "logs")
        if not os.path.isdir(logs_dir):
            os.mkdir(logs_dir)
        log_path = os.path.join(logs_dir, log_file)

        if self.log_handler in logger.handlers:
            logger.removeHandler(self.log_handler)
        self.log_handler = logging.FileHandler(log_path)

        formatter = logging.Formatter(
            "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.log_handler)
        logger.info("%s set up a log file at %s", self.name, log_file)
        logger.info("%s is starting a test for %s", self.name, self.project.name.get())

    def to_log(self, msg) -> None:
        """Pass a message to the log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def set_view(self, view: ttk.Frame) -> None:
        """Stores a ref to the view displaying the handler."""
        self.view = view
