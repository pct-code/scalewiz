"""Evaluation window for a Project."""

from __future__ import annotations

import os
import time
import tkinter as tk
import typing
from tkinter import font, ttk

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator

from pct_scalewiz.components.base_frame import BaseFrame
from pct_scalewiz.components.test_evaluation_row import TestResultRow
from pct_scalewiz.helpers.export_csv import export_csv
from pct_scalewiz.models.project import Project

if typing.TYPE_CHECKING:
    from pct_scalewiz.models.test_handler import TestHandler

COLORS = [
    "orange",
    "blue",
    "red",
    "mediumseagreen",
    "darkgoldenrod",
    "indigo",
    "mediumvioletred",
    "darkcyan",
    "maroon",
    "darkslategrey",
]


class EvaluationFrame(BaseFrame):
    """Frame for analyzing data."""

    def __init__(self, parent: tk.Toplevel, handler: TestHandler) -> None:
        BaseFrame.__init__(self, parent)
        self.handler = handler
        # todo #8 refactor this. need to rename across all the ProjectX classes
        self.project = handler.project
        parent.winfo_toplevel().title(self.project.name.get())
        self.build()

    def trace(self) -> None:
        """Applies a tkVar trace to properties on every test object."""
        for test in self.project.tests:
            test.label.trace("w", self.score)
            test.pump_to_score.trace("w", self.score)
            test.include_on_report.trace("w", self.score)

    def render(self, label: tk.Widget, entry: tk.Widget, row: int) -> None:
        """Renders a given label and entry on the passed row."""
        # pylint: disable=no-self-use
        label.grid(row=row, column=0, sticky="e")
        entry.grid(row=row, column=1, sticky="new", padx=(5, 550), pady=2)

    def build(self) -> None:
        """Destroys all child widgets, then builds the UI."""
        for child in self.winfo_children():
            child.destroy()

        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=0, column=0)

        tests_frame = ttk.Frame(self)

        bold_font = font.Font(family="Arial", weight="bold", size=10)
        # header row
        labels = []
        labels.append(tk.Label(tests_frame, text="Name", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Label", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Minutes", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Pump", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Baseline", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Max", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Clarity", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Notes", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Result", font=bold_font))
        labels.append(tk.Label(tests_frame, text="Report", font=bold_font))
        for i, label in enumerate(labels):
            label.grid(row=0, column=i, padx=3, sticky="w")

        self.grid_columnconfigure(0, weight=1)
        # add traces for scoring
        self.trace()

        self.blanks = []
        for test in self.project.tests:
            if test.is_blank.get():
                self.blanks.append(test)

        # select the trials
        self.trials = []
        for test in self.project.tests:
            if not test.is_blank.get():
                self.trials.append(test)

        tk.Label(tests_frame, text="Blanks:", font=bold_font).grid(
            row=1, column=0, sticky="w", padx=3, pady=1
        )
        tk.Label(tests_frame, text="Trials:", font=bold_font).grid(
            row=2 + len(self.blanks), column=0, sticky="w", padx=3, pady=1
        )

        for i, blank in enumerate(self.blanks):
            TestResultRow(tests_frame, blank, self.project, i + 2).grid(
                row=i + 1, column=0, sticky="w", padx=3, pady=1
            )
        count = len(self.blanks)
        for i, trial in enumerate(self.trials):
            TestResultRow(tests_frame, trial, self.project, i + count + 3).grid(
                row=i + count + 3, column=0, sticky="w", padx=3, pady=1
            )

        self.tab_control.add(tests_frame, text="   Data   ")

        # plot stuff ----------------------------------------------------------
        self.plot()

        # evaluation stuff ----------------------------------------------------
        log_frame = ttk.Frame(self)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = tk.scrolledtext.ScrolledText(
            log_frame, background="white", state="disabled"
        )
        self.log_text.grid(sticky="ew")
        self.tab_control.add(log_frame, text="   Calculations   ")

        button_frame = ttk.Frame(self)
        ttk.Button(
            button_frame, text="Save", command=lambda: self.save(), width=10
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            button_frame,
            text="Export",
            command=lambda: export_csv(self.project),
            width=10,
        ).grid(row=0, column=1, padx=5)
        button_frame.grid(row=1, column=0, pady=5)
        # update results
        self.score()

    def plot(self) -> None:
        """Destroys the old plot frame if it exists, then makes a new one."""
        # close all pyplots to prevent memory leak
        plt.close("all")
        # get rid of our old plot tab if we have one
        if hasattr(self, "plot_frame"):
            self.plot_frame.destroy()

        self.plot_frame = ttk.Frame(self.tab_control)
        self.fig, self.axis = plt.subplots(figsize=(7.5, 4), dpi=100)
        self.fig.patch.set_facecolor("#FAFAFA")
        plt.subplots_adjust(wspace=0, hspace=0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        with plt.style.context("bmh"):
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=COLORS)
            self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
            self.axis.set_facecolor("w")
            self.axis.clear()

            # plot everything
            for blank in self.blanks:
                if blank.include_on_report.get():
                    elapsed = []
                    for reading in blank.readings:
                        elapsed.append(reading["elapsedMin"])
                    self.axis.plot(
                        elapsed,
                        blank.get_readings(),
                        label=blank.label.get(),
                        linestyle=("-."),
                    )

            for trial in self.trials:
                if trial.include_on_report.get():
                    elapsed = []
                    for i, reading in enumerate(trial.readings):
                        elapsed.append(trial.readings[i]["elapsedMin"])
                    self.axis.plot(
                        elapsed, trial.get_readings(), label=trial.label.get()
                    )

            self.axis.set_xlabel("Time (min)")
            self.axis.set_ylabel("Pressure (psi)")
            self.axis.set_ylim(top=self.project.limit_psi.get())
            self.axis.yaxis.set_major_locator(MultipleLocator(100))
            self.axis.set_xlim((0, self.project.limit_minutes.get()))
            self.axis.legend(loc=0)
            self.axis.margins(0)
            plt.tight_layout()

        # finally, add to parent control
        self.tab_control.add(self.plot_frame, text="   Plot   ")
        self.tab_control.insert(1, self.plot_frame)

    def save(self) -> None:
        """Saves the project to file, as well as the most recent plot and calculations log."""
        # update image
        out = f"{self.project.numbers.get().replace(' ', '')} {self.project.name.get()} Scale Block Analysis (Graph).png"
        out = os.path.join(os.path.dirname(self.project.path.get()), out)
        self.fig.savefig(out)
        self.project.plot.set(out)
        # update log
        out = f"{self.project.numbers.get().replace(' ', '')} {self.project.name.get()} Scale Block Analysis (Log).txt"
        out = os.path.join(os.path.dirname(self.project.path.get()), out)
        log = self.log_text.get("1.0", "end-1c")
        with open(out, "w") as file:
            file.write(log)

        Project.dump_json(self.project, self.project.path.get())
        self.handler.project = self.project = Project.load_json(self.project.path.get())

        self.build()

    def score(self, *args) -> None:
        """Updates the result for every Test in the Project. Accepts event args passed from the tkVar trace."""
        start_time = time.time()
        self.log = []
        # scoring props

        max_readings = round(
            self.project.limit_minutes.get() * 60 / self.project.interval.get()
        )
        self.log.append("Max readings: limitMin * 60 / reading interval")
        self.log.append(f"Max readings: {max_readings}")
        baseline_area = round(self.project.baseline.get() * max_readings)
        self.log.append("Baseline area: baseline PSI * max readings")
        self.log.append(
            f"Baseline area: {self.project.baseline.get()} * {max_readings}"
        )
        self.log.append(f"Baseline area: {baseline_area}")
        self.log.append("-" * 80)
        self.log.append("")

        # select the blanks
        blanks = []
        for test in self.project.tests:
            if test.is_blank.get() and test.include_on_report.get():
                blanks.append(test)

        if len(blanks) < 1:
            return

        areas_over_blanks = []
        for blank in blanks:
            self.log.append(f"Evaluating {blank.name.get()}")
            self.log.append(f"Considering data: {blank.pump_to_score.get()}")
            readings = blank.get_readings()
            self.log.append(f"Total readings: {len(readings)}")
            int_psi = sum(readings)
            self.log.append("Integral PSI: sum of all pressure readings")
            self.log.append(f"Integral PSI: {int_psi}")
            area = self.project.limit_psi.get() * len(readings) - int_psi
            self.log.append("Area over blank: limit_psi * # of readings - integral PSI")
            self.log.append(
                f"Area over blank: {self.project.limit_psi.get()} * {len(readings)} - {int_psi}"
            )
            self.log.append(f"Area over blank: {area}")
            self.log.append("")
            areas_over_blanks.append(area)

        # get protectable area
        avg_blank_area = round(sum(areas_over_blanks) / len(areas_over_blanks))
        self.log.append(f"Average area over blanks: {avg_blank_area}")
        avg_protectable_area = (
            self.project.limit_psi.get() * max_readings - avg_blank_area
        )
        self.log.append(
            "Average protectable area: limit_psi * max_readings - average area over blanks"
        )
        self.log.append(
            f"Average protectable area: {self.project.limit_psi.get()} * {max_readings} - {avg_blank_area}"
        )
        self.log.append(f"Average protectable area: {avg_protectable_area}")
        self.log.append("-" * 80)
        self.log.append("")

        # select trials
        trials = []
        for test in self.project.tests:
            if not test.is_blank.get():
                trials.append(test)

        # get readings
        for trial in trials:
            self.log.append(f"Evaluating {trial.name.get()}")
            self.log.append(f"Considering data: {trial.pump_to_score.get()}")
            readings = trial.get_readings()
            self.log.append(f"Total readings: {len(readings)}")
            int_psi = sum(readings) + (
                (max_readings - len(readings)) * self.project.limit_psi.get()
            )
            self.log.append("Integral PSI: sum of all pressure readings")
            self.log.append(f"Integral PSI: {int_psi}")
            result = round(1 - (int_psi - baseline_area) / avg_protectable_area, 3)
            self.log.append(
                "Result: 1 - (integral PSI - baseline area) / avg protectable area"
            )
            self.log.append(
                f"Result: 1 - ({int_psi} - {baseline_area}) / {avg_protectable_area}"
            )
            self.log.append(f"Result: {result}")
            self.log.append("")
            trial.result.set(result)

        self.plot()
        self.log.append("-" * 80)

        self._log = self.log
        self.log = []
        self.log.append(f"Evaluating results for {self.project.name.get()}...")
        self.log.append("")
        self.log.append(f"Finished in {round(time.time() - start_time, 3)} s")
        self.log.append("-" * 80)
        self.log.append("")
        self.log = self.log + self._log
        self.to_log(self.log)

    def to_log(self, log: list[str]) -> None:
        """Adds the passed log message to the Text widget in the Calculations frame."""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, "end")
        for i in log:
            self.log_text.insert("end", i)
            self.log_text.insert("end", "\n")
        self.log_text.configure(state="disabled")