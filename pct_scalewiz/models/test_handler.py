"""Handles a test."""

from __future__ import annotations

import logging
import os
import time
import tkinter as tk
import typing
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from tkinter import filedialog, messagebox

from serial import Serial, SerialException

from pct_scalewiz.models.project import Project
from pct_scalewiz.models.teledyne_pump import TeledynePump
from pct_scalewiz.models.test import Test

if typing.TYPE_CHECKING:
    from tkinter.scrolledtext import ScrolledText

logger = logging.getLogger("scalewiz")


class TestHandler:
    """Handles a Test."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name: str = "Nemo") -> None:
        self.name = name
        self.project = Project()
        self.test = Test()
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.queue: list[dict] = []
        self.editors = []  # list of views displaying the project
        self.max_readings = int()  # max # of readings to collect
        self.max_pressures: dict[str, int] = {"pump 1": int(), "pump 2": int()}
        # we assign a real handler later
        self.log_handler: logging.FileHandler = None
        # test handler view overwrites this attribute with a widget
        self.log_text: ScrolledText = None

        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stop_requested = False
        self.progress = tk.IntVar()
        self.elapsed = tk.StringVar()

        self.pump1: TeledynePump = None
        self.pump2: TeledynePump = None

        # todo #7 refactor needed. this can't account for rinse/uptake cycles
        # need new way to manage state
        # UI concerns
        self.is_running = tk.BooleanVar()
        self.is_done = tk.BooleanVar()

    def get_can_run(self) -> bool:
        """Returns a bool indicating whether or not the test can run."""
        return (
            (
                self.max_pressures["pump 1"] <= self.project.limit_psi.get()
                or self.max_pressures["pump 2"] <= self.project.limit_psi.get()
            )
            and len(self.queue) < self.max_readings
            and not self.stop_requested
        )

    def load_project(self, path: str = None) -> None:
        """Opens a file dialog then loads the selected Project file."""
        if path is None:
            path = filedialog.askopenfilename(
                initialdir='C:"',
                title="Select project file:",
                filetypes=[("JSON files", "*.json")],
            )

        if path != "":
            self.project = Project()
            self.project.load_json(path)
            self.rebuild_editors()
            logger.info("Loaded %s to %s", self.project.name.get(), self.name)

        self.max_readings = (
            round(self.project.limit_minutes.get() * 60 / self.project.interval.get())
            + 1
        )

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""
        # pylint: disable=too-many-return-statements
        # this IS too many returns, but easier than a refactor
        if self.is_running.get():
            return

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

        if not os.path.exists(self.project.path.get()):
            msg = "Select an existing project file first"
            messagebox.showwarning("Invalid Project Selected", msg)
            return

        if self.test.name.get() == "":
            msg = "Name the experiment before starting"
            messagebox.showwarning("Invalid Experiment Name", msg)
            return

        if self.test.clarity.get() == "" and not self.test.is_blank.get():
            msg = "Water clarity cannot be blank"
            messagebox.showwarning("Missing Water Clarity", msg)
            return

        self.setup_pumps()

        if not self.pump1.port.isOpen():
            msg = f"Couldn't connect to {self.pump1.port.name}"
            messagebox.showwarning("Serial Exception", msg)
            return

        if not self.pump2.port.isOpen():
            msg = f"Couldn't connect to {self.pump2.port.name}"
            messagebox.showwarning("Serial Exception", msg)
            return

        # close any open editors
        self.rebuild_editors()
        self.stop_requested = False
        self.is_done.set(False)
        self.is_running.set(True)
        self.progress.set(0)
        self.elapsed.set("")
        # make a new log file
        log_path = f"{round(time.time())}_{self.test.name.get()}_{date.today()}.txt"
        parent_dir = os.path.dirname(self.project.path.get())
        logs_dir = os.path.join(parent_dir, "logs")
        if not os.path.isdir(logs_dir):
            os.mkdir(logs_dir)
        log_file = os.path.join(logs_dir, log_path)

        # update the file handler
        self.update_log_handler(log_file)
        self.pool.submit(self.take_readings)

    def update_log_handler(self, log_file: str) -> None:
        """Sets up the logging FileHandler to the passed path."""
        if self.log_handler in logger.handlers:
            logger.removeHandler(self.log_handler)
        self.log_handler = logging.FileHandler(log_file)

        formatter = logging.Formatter(
            "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.log_handler)
        logger.info("%s set up a log file at %s", self.name, log_file)
        logger.info("%s is starting a test for %s", self.name, self.project.name.get())

    def take_readings(self) -> None:
        """Get ready to take readings, then start doing it on a second thread."""
        # set default values for this instance of the test loop
        self.queue = []
        self.max_pressures["pump 1"] = self.max_pressures["pump 2"] = 0
        # start the pumps
        self.pump1.run()
        self.pump2.run()
        # run the uptake cycle
        uptake = self.project.uptake.get()
        for i in range(uptake):
            if self.get_can_run():
                self.elapsed.set(f"{uptake - i} s")
                self.progress.set(round(i / uptake * 100))
                time.sleep(1)
            else:
                self.stop_test()
                break

        self.to_log("")
        interval = self.project.interval.get()
        snooze = round(interval * 0.75, 2)

        test_start_time = time.monotonic()
        reading_start = test_start_time - interval

        # readings loop -------------------------------------------------------
        while self.get_can_run():
            if time.monotonic() - reading_start >= interval:
                reading_start = time.monotonic()
                minutes_elapsed = round((time.monotonic() - test_start_time) / 60, 2)

                psi1 = self.pump1.get_pressure()
                psi2 = self.pump2.get_pressure()
                collected = time.monotonic() - reading_start
                logger.debug("%s collected both PSIs in %s s", self.name, collected)
                average = round(((psi1 + psi2) / 2))

                reading = {
                    "elapsedMin": minutes_elapsed,
                    "pump 1": psi1,
                    "pump 2": psi2,
                    "average": average,
                }

                # make a message for the log in the test handler view
                msg = "@ {:.2f} min; pump1: {}, pump2: {}, avg: {}".format(
                    minutes_elapsed, psi1, psi2, average
                )
                self.to_log(msg)
                logger.info("%s - %s", self.name, msg)

                # todo use a real Queue ??
                self.queue.append(reading)

                self.elapsed.set(f"{minutes_elapsed:.2f} min.")
                self.progress.set(round(len(self.queue) / self.max_readings * 100))

                if psi1 > self.max_pressures["pump 1"]:
                    self.max_pressures["pump 1"] = psi1
                if psi2 > self.max_pressures["pump 2"]:
                    self.max_pressures["pump 2"] = psi2
                logger.debug(
                    "Finished doing everything else in %s s",
                    time.monotonic() - reading_start - collected,
                )
                logger.debug(
                    "%s collected data in %s",
                    self.name,
                    time.monotonic() - reading_start,
                )
                time.sleep(snooze)
        # end of readings loop ------------------------------------------------

        # find the actual elapsed time
        actual_elapsed = round((time.monotonic() - test_start_time) / 60, 2)
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
                len(self.queue) / self.max_readings,
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
        if self.pump1.port.isOpen():
            self.pump1.stop()
            self.pump1.close()
            logger.info(
                "%s: Stopped and closed the device @ %s",
                self.name,
                self.pump1.port.port,
            )

        if self.pump2.port.isOpen():
            self.pump2.stop()
            self.pump2.close()
            logger.info(
                "%s: Stopped and closed the device @ %s",
                self.name,
                self.pump1.port.port,
            )

        self.is_done.set(True)

        logger.info("%s: Test for %s has been stopped", self.name, self.test.name.get())

    def save_test(self) -> None:
        """Saves the test to the Project file in JSON format."""
        for reading in self.queue:
            self.test.readings.append(reading)
        self.queue.clear()
        self.project.tests.append(self.test)
        self.project.dump_json()
        self.load_project(path=self.project.path.get())
        self.rebuild_editors()

    def setup_pumps(self) -> None:
        """Set up the pumps with some default values."""
        # the timeout values are an alternative to using TextIOWrapper
        # the values chosen were suggested by the pump's documentation
        try:
            port1 = Serial(self.dev1.get(), timeout=0.05)
            self.pump1 = TeledynePump(port1, logger=logger)
            logger.info("%s: established a connection to %s", self.name, port1.port)

            port2 = Serial(self.dev2.get(), timeout=0.05)
            self.pump2 = TeledynePump(port2, logger=logger)
            logger.info("%s: established a connection to %s", self.name, port2.port)

        except SerialException as error:
            logger.exception(error)
            messagebox.showwarning("Serial Exception", error)

    # methods that affect UI
    def new_test(self) -> None:
        """Initialize a new test."""
        logger.info("%s: Initialized a new test", self.name)
        self.test = Test()
        self.is_running.set(False)
        self.is_done.set(False)
        self.progress.set(0)
        self.elapsed.set("")
        # rebuild the TestHandlerView
        # todo #14 don't do this. where is parent assigned??
        self.parent.build()

    def rebuild_editors(self) -> None:
        """Rebuild all open Toplevels that could overwrite the Project file."""
        for window in self.editors:
            if window.winfo_exists() == 1:
                window.build(reload=True)
        logger.info("%s has rebuilt all editor windows", self.name)

    def to_log(self, msg) -> None:
        """Pass a message to the log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
