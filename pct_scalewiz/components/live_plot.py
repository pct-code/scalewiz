"""Renders data from a TestHandler as it is collected."""

from __future__ import annotations

import logging
import time
import typing
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.ticker import MultipleLocator

if typing.TYPE_CHECKING:
    from pct_scalewiz.models.test_handler import TestHandler

logger = logging.getLogger("scalewiz")


class LivePlot(ttk.Frame):
    """Renders data from a TestHandler as it is collected."""

    def __init__(self, parent: ttk.Frame, handler: TestHandler) -> None:
        """Initialize a LivePlot."""
        ttk.Frame.__init__(self, parent)
        self.handler = handler

        # matplotlib objects
        fig, self.axis = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor("#FAFAFA")
        self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
        self.axis.set_facecolor("w")
        # self.axis.set_ylim(top=self.handler.project.limit_psi.get())
        # self.axis.yaxis.set_major_locator(MultipleLocator(100))
        # self.axis.set_xlim((0, None), auto=True)
        self.axis.margins(0)
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.97, top=0.95)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        interval = handler.project.interval.get() * 1000  # ms
        self.ani = FuncAnimation(fig, self.animate, interval=interval)

    def animate(self, interval: float) -> None:
        """Animates the live plot if a test isn't running."""
        # the interval argument is used by matplotlib internally

        # we can just skip this if the test isn't running
        if self.handler.is_running.get() and not self.handler.is_done.get():
            # data access here 😳
            start = time.time()
            logger.debug("%s: Drawing a new plot ...", self.handler.name)
            with plt.style.context("bmh"):
                self.axis.clear()
                self.axis.set_xlabel("Time (min)")
                self.axis.set_ylabel("Pressure (psi)")
                pump1 = []
                pump2 = []
                elapsed = []  # we will share this series as an axis
                for reading in self.handler.queue:
                    pump1.append(reading["pump 1"])
                    pump2.append(reading["pump 2"])
                    elapsed.append(reading["elapsedMin"])
                self.axis.plot(elapsed, pump1, label="Pump 1")
                self.axis.plot(elapsed, pump2, label="Pump 2")
                self.axis.legend(loc=0)
                logger.debug(
                    "%s: Drew a new plot for %s data points in %s s",
                    self.handler.name,
                    len(self.handler.queue),
                    round(time.time() - start, 3),
                )
