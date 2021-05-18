"""Evaluation window for a Project."""

from __future__ import annotations

import time
import tkinter as tk
from logging import getLogger
from pathlib import Path
from tkinter import font, ttk
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator

from scalewiz.components.test_evaluation_row import TestResultRow
from scalewiz.helpers.export_csv import export_csv
from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.project import Project

if TYPE_CHECKING:
    from typing import Set

    from scalewiz.models.test import Test
    from scalewiz.models.test_handler import TestHandler


COLORS = (
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
)

LOGGER = getLogger("scalewiz")


class EvaluationWindow(tk.Toplevel):
    """Frame for analyzing data."""

    def __init__(self, handler: TestHandler) -> None:
        tk.Toplevel.__init__(self)
        self.handler = handler
        self.editor_project = Project()
        if Path(self.handler.project.path.get()).is_file:
            self.editor_project.load_json(self.handler.project.path.get())
        # matplotlib uses these later
        self.fig, self.axis, self.canvas = None, None, None
        self.plot_frame: ttk.Frame = None  # this gets destroyed in plot()
        self.trials: Set[Test] = set()
        self.blanks: Set[Test] = set()
        self.build()

    def render(self, label: tk.Widget, entry: tk.Widget, row: int) -> None:
        """Renders a given label and entry on the passed row."""
        # pylint: disable=no-self-use
        label.grid(row=row, column=0, sticky="e")
        entry.grid(row=row, column=1, sticky="new", padx=(5, 550), pady=2)

    def build(self, reload: bool = False) -> None:
        """Destroys all child widgets, then builds the UI."""
        if reload and Path(self.handler.project.path.get()).is_file:
            # cleanup for the GC
            for test in self.editor_project.tests:
                test.remove_traces()
            self.editor_project.remove_traces()
            self.editor_project = Project()
            self.editor_project.load_json(self.handler.project.path.get())

        self.winfo_toplevel().title(
            f"{self.handler.name} {self.handler.project.name.get()}"
        )
        set_icon(self)

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

        self.blanks.clear()
        self.trials.clear()
        #  filter through blanks and trials
        for test in self.editor_project.tests:
            if test.is_blank.get():
                self.blanks.add(test)
            else:
                self.trials.add(test)

        tk.Label(tests_frame, text="Blanks:", font=bold_font).grid(
            row=1, column=0, sticky="w", padx=3, pady=1
        )
        tk.Label(tests_frame, text="Trials:", font=bold_font).grid(
            row=2 + len(self.blanks), column=0, sticky="w", padx=3, pady=1
        )

        for i, blank in enumerate(self.blanks):
            TestResultRow(tests_frame, blank, self.editor_project, i + 2).grid(
                row=i + 1, column=0, sticky="w", padx=3, pady=1
            )
        count = len(self.blanks)
        for i, trial in enumerate(self.trials):
            TestResultRow(tests_frame, trial, self.editor_project, i + count + 3).grid(
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
        ttk.Button(button_frame, text="Save", command=self.save, width=10).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(
            button_frame,
            text="Export",
            command=lambda: export_csv(self.editor_project),
            width=10,
        ).grid(row=0, column=1, padx=5)
        button_frame.grid(row=1, column=0, pady=5)
        # update results
        self.score()

    def plot(self) -> None:
        """Destroys the old plot frame if it exists, then makes a new one."""
        # close all pyplots to prevent memory leak
        plt.close("all")
        # get rid of our old plot tab
        if isinstance(self.plot_frame, ttk.Frame):
            self.plot_frame.destroy()
        self.plot_frame = ttk.Frame(self)
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
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(
                        elapsed,
                        blank.get_readings(),
                        label=blank.label.get(),
                        linestyle=("-."),
                    )

            for trial in self.trials:
                if trial.include_on_report.get():
                    elapsed = []
                    for reading in trial.readings:
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(
                        elapsed, trial.get_readings(), label=trial.label.get()
                    )

            self.axis.set_xlabel("Time (min)")
            self.axis.set_ylabel("Pressure (psi)")
            self.axis.set_ylim(top=self.editor_project.limit_psi.get())
            self.axis.yaxis.set_major_locator(MultipleLocator(100))
            self.axis.set_xlim((0, self.editor_project.limit_minutes.get()))
            self.axis.legend(loc=0)
            self.axis.margins(0)
            plt.tight_layout()

        # finally, add to parent control
        self.tab_control.add(self.plot_frame, text="   Plot   ")
        self.tab_control.insert(1, self.plot_frame)

    def save(self) -> None:
        """Saves to file the project, most recent plot, and calculations log."""
        # update image
        plot_output = (
            f"{self.editor_project.numbers.get().replace(' ', '')} "
            f"{self.editor_project.name.get()} "
            "Scale Block Analysis (Graph).png"
        )
        parent_dir = Path(self.editor_project.path.get()).parent
        plot_output = Path(parent_dir, plot_output).resolve()
        self.fig.savefig(plot_output)
        self.editor_project.plot.set(str(plot_output))
        # update log
        log_output = (
            f"{self.editor_project.numbers.get().replace(' ', '')} "
            f"{self.editor_project.name.get()} "
            "Scale Block Analysis (Log).txt"
        ).strip()
        log_output = Path(parent_dir, log_output).resolve()

        with log_output.open("w") as file:
            file.write(self.log_text.get("1.0", "end-1c"))

        self.editor_project.dump_json()
        self.handler.rebuild_views()
        self.handler.load_project(self.editor_project.path.get())

    def score(self, *args) -> None:
        """Updates the result for every Test in the Project.

        Accepts event args passed from the tkVar trace.
        """
        # extra unused args are passed in by tkinter
        start_time = time.time()
        log = []
        # scoring props
        limit_minutes = self.editor_project.limit_minutes.get()
        interval_seconds = self.editor_project.interval_seconds.get()
        max_readings = round(limit_minutes * 60 / interval_seconds)
        log.append("Max readings: limitMin * 60 / reading interval")
        log.append(f"Max readings: {max_readings}")
        baseline_area = round(self.editor_project.baseline.get() * max_readings)
        log.append("Baseline area: baseline PSI * max readings")
        log.append(
            f"Baseline area: {self.editor_project.baseline.get()} * {max_readings}"
        )
        log.append(f"Baseline area: {baseline_area}")
        log.append("-" * 80)
        log.append("")

        # select the blanks
        blanks = []
        for test in self.editor_project.tests:
            if test.is_blank.get() and test.include_on_report.get():
                blanks.append(test)

        areas_over_blanks = []
        for blank in blanks:
            log.append(f"Evaluating {blank.name.get()}")
            log.append(f"Considering data: {blank.pump_to_score.get()}")
            readings = blank.get_readings()
            log.append(f"Total readings: {len(readings)}")
            log.append(f"Observed baseline: {blank.observed_baseline.get()} psi")
            int_psi = sum(readings)
            log.append("Integral PSI: sum of all pressure readings")
            log.append(f"Integral PSI: {int_psi}")
            area = self.editor_project.limit_psi.get() * len(readings) - int_psi
            log.append("Area over blank: limit_psi * # of readings - integral PSI")
            log.append(
                f"Area over blank: {self.editor_project.limit_psi.get()} "
                f"* {len(readings)} - {int_psi}"
            )
            log.append(f"Area over blank: {area}")
            log.append("")
            areas_over_blanks.append(area)

        if len(areas_over_blanks) < 1:
            return
        # get protectable area
        avg_blank_area = round(sum(areas_over_blanks) / len(areas_over_blanks))
        log.append(f"Avg. area over blanks: {avg_blank_area}")
        avg_protectable_area = (
            self.editor_project.limit_psi.get() * max_readings - avg_blank_area
        )
        log.append(
            "Avg. protectable area: limit_psi * max_readings - avg. area over blanks"
        )
        log.append(
            f"Avg. protectable area: {self.editor_project.limit_psi.get()} "
            f"* {max_readings} - {avg_blank_area}"
        )
        log.append(f"Avg. protectable area: {avg_protectable_area}")
        log.append("-" * 80)
        log.append("")

        # select trials
        trials = []
        for test in self.editor_project.tests:
            if not test.is_blank.get():
                trials.append(test)

        # get readings
        for trial in trials:
            log.append(f"Evaluating {trial.name.get()}")
            log.append(f"Considering data: {trial.pump_to_score.get()}")
            readings = trial.get_readings()
            log.append(f"Total readings: {len(readings)}")
            log.append(f"Observed baseline: {trial.observed_baseline.get()} psi")
            int_psi = sum(readings) + (
                (max_readings - len(readings)) * self.editor_project.limit_psi.get()
            )
            log.append("Integral PSI: sum of all pressure readings")
            log.append(f"Integral PSI: {int_psi}")
            result = round(1 - (int_psi - baseline_area) / avg_protectable_area, 3)
            log.append(
                "Result: 1 - (integral PSI - baseline area) / avg protectable area"
            )
            log.append(
                f"Result: 1 - ({int_psi} - {baseline_area}) / {avg_protectable_area}"
            )
            log.append(f"Result: {result} \n")
            trial.result.set(result)

        self.plot()

        log.insert(0, f"Evaluating results for {self.editor_project.name.get()}...")
        log.insert(1, f"Finished in {round(time.time() - start_time, 3)} s \n")
        self.to_log(log)

    def to_log(self, log: list[str]) -> None:
        """Adds the passed log message to the Text widget in the Calculations frame."""
        if self.log_text.grid_info() != {}:
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")
            for msg in log:
                self.log_text.insert("end", "".join((msg, "/n")))
            self.log_text.configure(state="disabled")
