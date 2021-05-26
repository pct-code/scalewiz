"""A Tkinter widget for handling tests."""

from __future__ import annotations

from logging import getLogger
from tkinter import ttk
from typing import TYPE_CHECKING

from matplotlib import pyplot as plt

from scalewiz.components.devices_comboboxes import DeviceBoxes
from scalewiz.components.live_plot import LivePlot
from scalewiz.components.test_controls import TestControls
from scalewiz.components.test_info_widget import TestInfo

if TYPE_CHECKING:

    from scalewiz.models.test_handler import TestHandler

LOGGER = getLogger("scalewiz")


class TestHandlerView(ttk.Frame):
    """A form for setting up / running Tests."""

    def __init__(self, parent: ttk.Frame, handler: TestHandler) -> None:
        super().__init__(parent)
        self.parent: ttk.Frame = parent
        self.handler: TestHandler = handler
        self.plot: LivePlot = None
        self.build()

    def build(self, *args) -> None:
        """Builds the UI, destroying any currently existing widgets."""
        if isinstance(self.plot, LivePlot):  # explicityly close to prevent memory leak
            self.after(0, plt.close, self.plot.fig)
        for child in self.winfo_children():
            child.destroy()
        self.grid_columnconfigure(0, weight=1)
        # row 0 ------------------------------------------------------------------------
        dev_ent = DeviceBoxes(self, self.handler)
        dev_ent.grid(row=0, column=0, sticky="new")

        # row 1 ------------------------------------------------------------------------
        frm = ttk.Frame(self)
        frm.grid_columnconfigure(1, weight=1)
        lbl = ttk.Label(frm, text="        Project:")
        lbl.grid(row=0, column=0, sticky="nw")
        proj = ttk.Label(frm, textvariable=self.handler.project.name, anchor="center")
        proj.grid(row=0, column=1, sticky="ew")
        frm.grid(row=1, column=0, sticky="new")

        # row 2 ------------------------------------------------------------------------
        test_info = TestInfo(self, self.handler)
        test_info.grid(row=2, column=0, sticky="new")

        # row 3-------------------------------------------------------------------------
        test_controls = TestControls(self, self.handler)
        test_controls.grid(row=3, column=0, sticky="nsew")

        # row 0 col 1 ------------------------------------------------------------------
        plt_frm = ttk.Frame(self)
        self.plot = LivePlot(plt_frm, self.handler)
        self.plot.grid(row=0, column=0, sticky="nsew")
        plt_frm.grid(row=0, column=1, rowspan=4)

    def update_input_frame(self) -> None:
        """Disables widgets in the input frame if a Test is running."""
        if self.handler.is_running:
            for widget in self.inputs:
                widget.configure(state="disabled")
        else:
            for widget in self.inputs:
                widget.configure(state="normal")
