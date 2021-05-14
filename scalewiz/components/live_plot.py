"""Renders data from a TestHandler as it is collected."""

from __future__ import annotations

import logging
import typing
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from matplotlib.ticker import MultipleLocator

if typing.TYPE_CHECKING:
    from scalewiz.models.test_handler import TestHandler

LOGGER = logging.getLogger("scalewiz")


class LivePlot(ttk.Frame):
    """Renders data from a TestHandler as it is collected."""

    def __init__(self, parent: ttk.Frame, handler: TestHandler) -> None:
        """Initialize a LivePlot."""
        super().__init__(parent)
        self.handler = handler

        # matplotlib objects
        plt.close("all")
        fig, self.axis = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor("#FAFAFA")
        self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
        self.axis.set_facecolor("w")  # white
        # self.axis.set_ylim(top=self.handler.project.limit_psi.get())
        # self.axis.yaxis.set_major_locator(MultipleLocator(100))
        # self.axis.set_xlim((0, None), auto=True)
        self.axis.margins(0)
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.97, top=0.95)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        interval = round(handler.project.interval_seconds.get() * 1000)  # ms
        self.ani = FuncAnimation(fig, self.animate, interval=interval)

    # could probably rewrite this with some tk.Widget.after calls
    def animate(self, interval: float) -> None:
        """Animates the live plot if a test isn't running."""
        # the interval argument is used by matplotlib internally

        # we can just skip this if the test isn't running
        if self.handler.is_running.get() and not self.handler.is_done.get():
            # data access here 😳
            readings = list(self.handler.readings.queue)
            if len(readings) > 0:
                LOGGER.debug("%s: Drawing a new plot ...", self.handler.name)
                with plt.style.context("bmh"):
                    self.axis.clear()
                    self.axis.set_xlabel("Time (min)")
                    self.axis.set_ylabel("Pressure (psi)")
                    pump1 = []
                    pump2 = []
                    elapsed = []  # we will share this series as an axis
                    for reading in readings:
                        pump1.append(reading.pump1)
                        pump2.append(reading.pump2)
                        elapsed.append(reading.elapsedMin)
                    self.axis.plot(elapsed, pump1, label="Pump 1")
                    self.axis.plot(elapsed, pump2, label="Pump 2")
                    self.axis.legend(loc=0)
