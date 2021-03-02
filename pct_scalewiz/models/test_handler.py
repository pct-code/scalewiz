"""Handles a test."""

import logging
import os
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from tkinter import filedialog, messagebox

from serial import Serial, SerialException

from pct_scalewiz.models.project import Project
from pct_scalewiz.models.teledyne_pump import TeledynePump
from pct_scalewiz.models.test import Test

logger = logging.getLogger("scalewiz")


class TestHandler:
    """Handles a Test."""

    def __init__(self, name: str = "Nemo") -> None:

        # pylint: disable=too-many-instance-attributes

        # local state vars
        self.name = name
        self.project = Project()
        self.test = Test()
        self.dev1 = tk.StringVar()
        self.dev2 = tk.StringVar()
        self.stop_requested = False
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.queue = []
        self.progress = tk.IntVar()
        self.elapsed = tk.StringVar()
        self.editors = []  # list of views displaying the project
        self.max_readings = int()

        # todo #7 refactor needed. this can't account for rinse/uptake cycles
        # need new way to manage state
        # UI concerns
        self.is_running = tk.BooleanVar()
        self.is_done = tk.BooleanVar()

        # logging
        # todo add handler here and set to a file in logs/ next to the project.json

    # todo stop doing this method pls
    def can_run(self) -> bool:
        """Returns a bool indicating whether or not the test can run."""
        value = (
            (
                self.max_psi_1 <= self.project.limit_psi.get()
                or self.max_psi_2 <= self.project.limit_psi.get()
            )
            and len(self.queue) < self.max_readings
            and not self.stop_requested
        )
        return value

    def load_project(self, path: str = None) -> None:
        """Opens a file dialog then loads the selected Project file."""
        if path is None:
            path = filedialog.askopenfilename(
                initialdir='C:"',
                title="Select project file:",
                filetypes=[("JSON files", "*.json")],
            )

        if path != "":
            self.close_editors()
            self.project = Project.load_json(path)
            logger.info(f"Loaded {self.project.name.get()} to {self.name}")

        self.max_readings = (
            round(self.project.limit_minutes.get() * 60 / self.project.interval.get())
            + 1
        )

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""

        # pylint: disable=too-many-return-statements
        # this IS too many returns, but easier than a refactor
        # wontfix

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

        if not os.path.isfile(self.project.path.get()):
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
        self.close_editors()
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
        if hasattr(self, "logFileHandler"):
            logger.removeHandler(self.log_handler)
        self.log_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.log_handler)
        logger.info(f"{self.name} set up a log file at {log_file}")
        logger.info(f"{self.name} is starting a test for {self.project.name.get()}")
        self.pool.submit(self.take_readings)

    def take_readings(self) -> None:
        """Get ready to take readings, then start doing it on a second thread."""
        # set default values for this instance of the test loop
        self.queue = []
        self.max_psi_1 = self.max_psi_2 = 0
        # start the pumps
        self.pump1.run()
        self.pump2.run()
        uptake = self.project.uptake.get()
        for i in range(uptake):
            if self.can_run():
                self.elapsed.set(f"{uptake - i} s")
                self.progress.set(round(i / uptake * 100))
                time.sleep(1)
            else:
                self.stop_test()
                break

        self.to_log("")
        interval = self.project.interval.get()
        snooze = round(interval * 0.9, 2)

        test_start_time = time.time()
        reading_start = test_start_time - interval

        # readings loop -------------------------------------------------------
        while self.can_run():
            if time.time() - reading_start >= interval:
                reading_start = time.time()
                minutes_elapsed = round((time.time() - test_start_time) / 60, 2)

                psi1 = self.pump1.get_pressure()
                psi2 = self.pump2.get_pressure()
                collected = time.time() - reading_start
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

                # todo this is janky
                self.queue.append(reading)

                self.elapsed.set(f"{minutes_elapsed:.2f} min.")
                self.progress.set(round(len(self.queue) / self.max_readings * 100))

                if psi1 > self.max_psi_1:
                    self.max_psi_1 = psi1
                if psi2 > self.max_psi_2:
                    self.max_psi_2 = psi2
                logger.debug(
                    "Finished doing everything else in %s s",
                    time.time() - reading_start - collected,
                )
                logger.debug(
                    "%s collected data in %s", self.name, time.time() - reading_start
                )
                # todo try asyncio - called defer or await or s/t
                time.sleep(snooze)
        # end of readings loop ------------------------------------------------

        # find the actual elapsed time
        actual_elapsed = round((time.time() - test_start_time) / 60, 2)
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
        Project.dump_json(self.project, self.project.path.get())
        logger.info(
            "%s: Saved %s to %s",
            self.name,
            self.project.name.get(),
            self.project.path.get(),
        )
        self.load_project(path=self.project.path.get())
        # todo ask them to rebuild instead
        self.close_editors()

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

    # todo give this a better name
    def close_editors(self) -> None:
        """Close all open Toplevels that could overwrite the Project file."""
        for window in self.editors:
            self.editors.remove(window)
            window.destroy()
        logger.info(f"{self.name} has closed all editor windows")

    def to_log(self, msg) -> None:
        """Pass a message to the log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
