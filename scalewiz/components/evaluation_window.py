"""Evaluation window for a Project."""

from __future__ import annotations

import tkinter as tk
from logging import getLogger
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, SubplotParams
from matplotlib.ticker import MultipleLocator

from scalewiz.components.evaluation_data_view import EvaluationDataView
from scalewiz.helpers.export_csv import export_csv
from scalewiz.helpers.score import score
from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.project import Project

if TYPE_CHECKING:

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
        super().__init__()
        self.handler = handler
        self.editor_project = Project()
        if Path(self.handler.project.path.get()).is_file:
            self.editor_project.load_json(self.handler.project.path.get())
        # matplotlib uses these later
        self.fig, self.axis, self.canvas = None, None, None  # matplotlib stuff
        self.log_text: ScrolledText = None
        self.plot_frame: ttk.Frame = None  # this gets destroyed in plot()
        self.title(f"{self.handler.name} {self.handler.project.name.get()}")
        self.resizable(0, 0)
        set_icon(self)
        self.build()

    def build(self, reload: bool = False) -> None:
        """Destroys all child widgets, then builds the UI."""
        if reload and Path(self.handler.project.path.get()).is_file:
            # cleanup for the GC
            for test in self.editor_project.tests:
                test.remove_traces()
            self.editor_project.remove_traces()
            self.editor_project = Project()
            self.editor_project.load_json(self.handler.project.path.get())

        for child in self.winfo_children():
            child.destroy()

        self.grid_columnconfigure(0, weight=1)
        # we will build a few tabs in this
        self.tab_control = ttk.Notebook(self, name="tab_control")
        self.tab_control.grid(row=0, column=0)

        data_view = EvaluationDataView(self.tab_control, self.editor_project)
        self.tab_control.add(data_view, text="   Data   ")

        # plot stuff ----------------------------------------------------------

        # evaluation stuff ----------------------------------------------------
        self.log_frame = ttk.Frame(self.tab_control, name="log_frame")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = ScrolledText(
            self.log_frame, background="white", state="disabled", name="log_text"
        )
        self.log_text.grid(sticky="nsew")
        self.tab_control.add(self.log_frame, text="   Calculations   ")
        self.plot()
        # finished adding to tab control

        button_frame = ttk.Frame(self)
        save_btn = ttk.Button(button_frame, text="Save", command=self.save, width=10)
        save_btn.grid(row=0, column=0, padx=5)
        export_btn = ttk.Button(
            button_frame,
            text="Export",
            command=lambda: export_csv(self.editor_project),
            width=10,
        )
        export_btn.grid(row=0, column=1, padx=5)
        button_frame.grid(row=1, column=0, pady=5)
        # update results
        score(self.editor_project, self.log_text)

    def plot(self) -> None:
        """Destroys the old plot frame if it exists, then makes a new one."""
        # close all pyplots to prevent memory leak
        if isinstance(self.fig, Figure):
            plt.close(self.fig)
        # get rid of our old plot tab
        if isinstance(self.plot_frame, ttk.Frame):
            self.plot_frame.destroy()

        self.plot_frame = ttk.Frame(self.tab_control, name="plot_frame")
        self.fig, self.axis = plt.subplots(
            figsize=(7.5, 4),
            dpi=100,
            subplotpars=SubplotParams(wspace=0, hspace=0),
        )
        self.fig.patch.set_facecolor("#FAFAFA")
        # plt.subplots_adjust(wspace=0, hspace=0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="none", expand=False)
        with plt.style.context("bmh"):
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=COLORS)
            self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
            self.axis.set_facecolor("w")  # white

            # plot blanks
            for blank in self.editor_project.tests:
                if blank.is_blank.get() and blank.include_on_report.get():
                    elapsed = []
                    for reading in blank.readings:
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(
                        elapsed,
                        blank.get_readings(),
                        label=blank.label.get(),
                        linestyle=("-."),
                    )
            # then plot trials
            for trial in self.editor_project.tests:
                if trial.include_on_report.get() and not trial.is_blank.get():
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
            self.axis.legend(loc="best")
            self.axis.margins(0)

        # finally, add to parent control
        self.tab_control.add(self.plot_frame, text="   Plot   ")
        self.tab_control.insert("end", self.plot_frame)

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

        # refresh
        self.editor_project.dump_json()
        self.handler.load_project(self.editor_project.path.get())
        self.handler.rebuild_views()

    def export(self) -> None:
        result, file = export_csv(self.editor_project)
        if result == 0:
            messagebox.showinfo("Export complete", f"Exported a report to {file}")
        else:
            messagebox.showwarning(
                "Export failed",
                (
                    f"Failed to export the report to {file}. \n"
                    "Check the log for a more detailed message."
                ),
            )
