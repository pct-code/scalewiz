"""Evaluation window for a Project."""

from __future__ import annotations

import tkinter as tk
from logging import getLogger
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from scalewiz.components.evaluation_data_view import EvaluationDataView
from scalewiz.components.evaluation_plot_view import EvaluationPlotView
from scalewiz.helpers.export_csv import export_csv
from scalewiz.helpers.score import score
from scalewiz.helpers.set_icon import set_icon
from scalewiz.models.project import Project

if TYPE_CHECKING:

    from scalewiz.models.test_handler import TestHandler


LOGGER = getLogger("scalewiz")


class EvaluationWindow(tk.Toplevel):
    """Frame for analyzing data."""

    def __init__(self, handler: TestHandler) -> None:
        super().__init__()
        self.handler = handler
        self.editor_project = Project()
        if Path(self.handler.project.path.get()).is_file():
            self.editor_project.load_json(self.handler.project.path.get())
        # matplotlib uses these later
        self.log_text: ScrolledText = None
        self.plot_view: EvaluationPlotView = None  # this gets destroyed in plot()
        self.title(f"{self.handler.name} {self.handler.project.name.get()}")
        self.resizable(0, 0)
        set_icon(self)
        self.build()

    def build(self, reload: bool = False) -> None:
        """Destroys all child widgets, then builds the UI."""
        if not self.winfo_exists():
            return

        if reload and Path(self.handler.project.path.get()).is_file():
            # cleanup for the GC
            self.editor_project.remove_traces()
            self.editor_project = Project()
            self.editor_project.load_json(self.handler.project.path.get())

        for child in self.winfo_children():
            if child.winfo_exists():
                self.after(0, child.destroy)

        self.grid_columnconfigure(0, weight=1)
        # we will build a few tabs in this
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=0, column=0)

        data_view = EvaluationDataView(self.tab_control, self.editor_project)
        self.tab_control.add(data_view, text="   Data   ")

        # plot stuff ----------------------------------------------------------

        # evaluation stuff ----------------------------------------------------
        self.log_frame = ttk.Frame(self.tab_control)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_text = ScrolledText(
            self.log_frame, background="white", state="disabled"
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
        if isinstance(self.plot_view, EvaluationPlotView):
            plt.close(self.plot_view.fig)
            self.plot_view.destroy()

        self.plot_view = EvaluationPlotView(self.tab_control, self.editor_project)
        self.tab_control.add(self.plot_view, text="   Plot   ")

    def save(self) -> None:
        """Saves to file the project, most recent plot, and calculations log."""
        if self.handler.is_running:
            messagebox.showwarning(
                "Can't save to this Project right now",
                "Can't save while a Test in this Project is running",
            )
            return

        # update image
        plot_output = (
            f"{self.editor_project.numbers.get().replace(' ', '')} "
            f"{self.editor_project.name.get()} "
            "Scale Block Analysis (Graph).png"
        )
        parent_dir = Path(self.editor_project.path.get()).parent
        plot_output = Path(parent_dir, plot_output).resolve()
        self.plot_view.fig.savefig(plot_output)
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
        self.after(0, self.handler.rebuild_views)

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
