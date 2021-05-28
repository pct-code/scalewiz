"""A plot view to be displayed in the Evaluation Window."""

from __future__ import annotations

import tkinter as tk
from logging import Logger, getLogger
from tkinter import Canvas, ttk
from tkinter.font import Font
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, SubplotParams
from matplotlib.ticker import MultipleLocator

if TYPE_CHECKING:
    from matplotlib.axis import Axis

    from scalewiz.models.project import Project

LOGGER: Logger = getLogger("scalewiz")

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


class EvaluationPlotView(ttk.Frame):
    """A widget for selecting devices."""

    def __init__(self, parent: ttk.Notebook, project: Project) -> None:
        super().__init__(parent)
        self.parent: ttk.Notebook = parent
        self.project: Project = project
        self.fig: Figure = None
        self.canvas: Canvas = None
        self.axis: Axis = None
        self.plot_frame: ttk.Frame = None
        self.build()

    def build(self) -> None:
        """Builds the UI."""
        if not self.winfo_exists():
            return

        if isinstance(self.fig, Figure):
            plt.close(self.fig)

        for child in self.winfo_children():
            if child.winfo_exists():
                child.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        label_frame = ttk.Frame(self)
        bold_font = Font(family="Arial", weight="bold", size=10)
        label_lbl = tk.Label(
            label_frame, text="Label", font=bold_font, width=20, anchor="center"
        )
        label_lbl.grid(row=0, column=0, sticky="ew")

        vcmd = self.register(self.update_plot)

        tests_on_report = []
        for test in self.project.tests:
            if test.include_on_report.get():
                tests_on_report.append(test)

        for test in tests_on_report:
            label_ent = ttk.Entry(
                label_frame,
                textvariable=test.label,
                validate="focusout",
                validatecommand=vcmd,
                width=25,
            )
            label_ent.grid(row=test.index.get() + 1, column=0, sticky="ew", pady=2)

        label_frame.grid(row=0, column=1, sticky="ns")

        print("plottings")

        self.plot_frame = ttk.Frame(self)
        self.fig, self.axis = plt.subplots(
            figsize=(7.5, 4),
            dpi=100,
            subplotpars=SubplotParams(wspace=0, hspace=0, top=0.95),
        )
        self.fig.patch.set_facecolor("#FAFAFA")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        with plt.style.context("bmh"):
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=COLORS)
            self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
            self.axis.set_facecolor("w")  # white

            # plot blanks
            for test in tests_on_report:
                if test.is_blank.get():
                    elapsed = []
                    for reading in test.readings:
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(
                        elapsed,
                        test.get_readings(),
                        label=test.label.get(),
                        linestyle=("-."),
                    )
            # then plot trials
            for test in tests_on_report:
                if not test.is_blank.get():
                    elapsed = []
                    for reading in test.readings:
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(elapsed, test.get_readings(), label=test.label.get())

            self.axis.set_xlabel("Time (min)")
            self.axis.set_ylabel("Pressure (psi)")
            self.axis.set_ylim(top=self.project.limit_psi.get())
            self.axis.yaxis.set_major_locator(MultipleLocator(100))
            self.axis.set_xlim((0, self.project.limit_minutes.get()))
            self.axis.legend(loc="best")
            self.axis.margins(0)

        self.plot_frame.grid(row=0, column=0, sticky="n")

    def update_plot(self) -> True:
        """Rebuilds the plot."""
        # running into a weird race condition when rebuilding...
        # this is a workaround
        self.after(0, self.build)
        self.after(100, self.build)
        return True
