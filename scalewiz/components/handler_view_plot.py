"""Renders data from a TestHandler as it is collected."""

from __future__ import annotations

import logging
from tkinter import ttk
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import SubplotParams

if TYPE_CHECKING:
    from scalewiz.models.test_handler import TestHandler

LOGGER = logging.getLogger("scalewiz")


class LivePlot(ttk.Frame):
    """Renders data from a TestHandler as it is collected."""

    def __init__(self, parent: ttk.Frame, handler: TestHandler) -> None:
        """Initialize a LivePlot."""
        super().__init__(parent)
        self.handler = handler
        self.build()

    def build(self) -> None:
        if not self.winfo_exists():
            return

        self.fig, self.axis = plt.subplots(
            figsize=(5, 3),
            dpi=100,
            constrained_layout=True,
            subplotpars=SubplotParams(left=0.1, bottom=0.1, right=0.95, top=0.95),
        )
        self.axis.set_xlabel("Time (min)")
        self.axis.set_ylabel("Pressure (psi)")
        self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
        self.axis.set_facecolor("w")  # white
        self.fig.patch.set_facecolor("#FAFAFA")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        interval = round(self.handler.project.interval_seconds.get() * 1000)  # -> ms
        self.ani = FuncAnimation(self.fig, self.animate, interval=interval)

    # could probably rewrite this with some tk.Widget.after calls
    def animate(self, interval: float) -> None:
        """Animates the live plot if a test isn't running.

        The interval argument is used by matplotlib internally.
        """
        # # we can just skip this if the test isn't running
        if len(self.handler.readings) > 0:
            if self.handler.is_running and not self.handler.is_done:
                pump1 = []
                pump2 = []
                elapsed = []  # we will share this series as an axis
                # cast to tuple in case the list changes during iteration
                readings = tuple(self.handler.readings)
                for reading in readings:
                    pump1.append(reading.pump1)
                    pump2.append(reading.pump2)
                    elapsed.append(reading.elapsedMin)
                max_psi = max((self.handler.max_psi_1, self.handler.max_psi_2))
                self.axis.clear()
                with plt.style.context("bmh"):
                    self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
                    self.axis.set_facecolor("w")  # white
                    self.axis.set_xlabel("Time (min)")
                    self.axis.set_ylabel("Pressure (psi)")
                    self.axis.set_ylim((0, max_psi + 50))
                    self.axis.margins(0, tight=True)
                    self.axis.plot(elapsed, pump1, label="Pump 1")
                    self.axis.plot(elapsed, pump2, label="Pump 2")
                    self.axis.legend(loc="best")
