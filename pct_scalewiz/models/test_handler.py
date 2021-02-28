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

    def __init__(self, name="Nemo") -> None:
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
            and len(self.queue) < self.max_readings()
            and not self.stop_requested
        )
        return value

    # todo why is this a method ????
    def max_readings(self) -> int:
        """Returns the maximum number of readings to take."""
        return (
            round(self.project.limit_minutes.get() * 60 / self.project.interval.get())
            + 1
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
            self.close_editors()
            self.project = Project.load_json(path)
            logger.info(f"Loaded {self.project.name.get()} to {self.name}")

    def start_test(self) -> None:
        """Perform a series of checks to make sure the test can run, then start it."""
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

        if self.test.clarity.get() == "":
            if self.test.is_blank.get():
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
        self.close_editors()
        self.stop_requested = False
        self.is_done.set(False)
        self.is_running.set(True)
        self.progress.set(0)
        # make a new log file
        log_path = f"{round(time.time())}_{self.test.name.get()}_{date.today()}.txt"
        parent_dir = os.path.dirname(self.project.path.get())
        logs_dir = os.path.join(parent_dir, "logs")
        if not os.path.isdir(logs_dir):
            os.mkdir(logs_dir)
        log_file = os.path.join(logs_dir, log_path)

        # update the file handler
        if hasattr(self, "logFileHandler"):
            logger.removeHandler(self.logFileHandler)
        self.logFileHandler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(thread)d - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        self.logFileHandler.setFormatter(formatter)
        self.logFileHandler.setLevel(logging.DEBUG)
        logger.addHandler(self.logFileHandler)
        logger.info(f"{self.name} set up a log file at {log_file}")
        logger.info(f"{self.name} is starting a test for {self.project.name.get()}")
        self.pool.submit(self.take_readings)

    def take_readings(self) -> None:
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
                logger.debug(f"{self.name} collected both PSIs in {collected} s")
                average = round(((psi1 + psi2) / 2))

                reading = {
                    "elapsedMin": minutes_elapsed,
                    "pump 1": psi1,
                    "pump 2": psi2,
                    "average": average,
                }

                # make a message for the log in the test handler view
                msg = f"@ {minutes_elapsed:.2f} min; pump1: {psi1}, pump2: {psi2}, avg: {average}"
                self.to_log(msg)
                logger.info(f"{self.name} - {msg}")

                # todo this is janky
                # why do this vs adding to test directly?
                # -> trying to not access same obj across threads
                self.queue.append(reading)

                self.elapsed.set(f"{minutes_elapsed:.2f} min.")
                self.progress.set(round(len(self.queue) / self.max_readings() * 100))

                if psi1 > self.max_psi_1:
                    self.max_psi_1 = psi1
                if psi2 > self.max_psi_2:
                    self.max_psi_2 = psi2
                logger.debug(
                    f"Finished doing everything else in {time.time() - reading_start - collected} s"
                )
                logger.debug(
                    f"{self.name} collected data in {time.time() - reading_start}"
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
                f"{self.name} - {minutes_elapsed} was really {actual_elapsed} ({len(self.queue)}/{self.max_readings()})"
            )

        self.stop_test()
        self.save_test()

    # because the readings loop is blocking, it is handled on a separate thread
    # beacuse of this, we have to interact with it in a somewhat backhanded way
    # this method is intended to be called from the test handler view module on a UI button click
    def requestStop(self) -> None:
        if not self.is_running.get():
            return

        if self.is_running.get():
            # the readings loop thread checks this flag on each iteration
            self.stop_requested = True
            logger.info(f"{self.name}: Received a stop request")

    def stop_test(self) -> None:
        if self.pump1.port.isOpen():
            self.pump1.stop()
            self.pump1.close()
            logger.info(
                f"{self.name}: Stopped and closed the device @ {self.pump1.port.port}"
            )

        if self.pump2.port.isOpen():
            self.pump2.stop()
            self.pump2.close()
            logger.info(
                f"{self.name}: Stopped and closed the device @ {self.pump1.port.port}"
            )

        self.is_done.set(True)
        self.progress.set(0)
        self.elapsed.set("")
        logger.info(f"{self.name}: Test for {self.test.name.get()} has been stopped")

    def save_test(self) -> None:
        for reading in self.queue:
            self.test.readings.append(reading)
        self.queue.clear()
        self.project.tests.append(self.test)
        Project.dump_json(self.project, self.project.path.get())
        logger.info(
            f"{self.name}: Saved {self.project.name.get()} to {self.project.path.get()}"
        )
        self.load_project(path=self.project.path.get())
        # todo ask them to rebuild instead
        self.close_editors()

    def setupPumps(self) -> None:
        """Set up the pumps with some default values."""
        # the timeout values are an alternative to using TextIOWrapper
        # the values chosen were suggested by the pump's documentation
        try:
            port1 = Serial(self.dev1.get(), timeout=0.05)
            self.pump1 = TeledynePump(port1, logger=logger)
            logger.info(f"{self.name}: established a connection to {port1.port}")

            port2 = Serial(self.dev2.get(), timeout=0.05)
            self.pump2 = TeledynePump(port2, logger=logger)
            logger.info(f"{self.name}: established a connection to {port2.port}")
        except SerialException as e:
            logger.exception(e)  # todo add more args ?
            messagebox.showwarning("Serial Exception", e)

    # methods that affect UI
    def new_test(self) -> None:
        """Initialize a new test."""
        logger.info(f"{self.name}: Initialized a new test")
        self.test = Test()
        self.is_running.set(False)
        self.is_done.set(False)
        self.elapsed.set("")
        # todo why is this here?
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
