"""A Tkinter widget for handling tests."""

from __future__ import annotations

import queue
import tkinter as tk
import typing
from logging import LogRecord, getLogger
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import matplotlib.pyplot as plt
import serial.tools.list_ports as list_ports

from scalewiz.components.live_plot import LivePlot

if typing.TYPE_CHECKING:
    from typing import List

    from scalewiz.models.test_handler import TestHandler

LOGGER = getLogger("scalewiz")


class TestHandlerView(ttk.Frame):
    """A form for setting up / running Tests."""

    def __init__(self, parent: ttk.Frame, handler: TestHandler) -> None:
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.handler = handler
        self.handler.parent = self
        self.devices_list: List[str] = []
        self.inputs: List[tk.Widget] = []
        self.inputs_frame: ttk.Frame = None
        self.device1_entry: ttk.Combobox = None
        self.device2_entry: ttk.Combobox = None
        self.trial_entry_frame: ttk.Frame = None
        self.blank_entry: ttk.Label = None
        self.blank_entry: ttk.Label = None
        self.start_button: ttk.Button = None
        self.new_button: ttk.Button = None
        self.elapsed_label: ttk.Label = None
        self.plot_frame: ttk.Frame = None
        self.log_frame: ttk.Frame = None
        self.log_text: ScrolledText = None
        # we don't have to worry about cleaning up these traces
        # the same handler instance will persist across projects
        self.handler.is_running.trace_add("write", self.update_input_frame)
        self.handler.is_done.trace_add("write", self.update_start_button)
        self.build()
        self.poll_log_queue()

    def build(self) -> None:
        """Builds the UI, destroying any currently existing widgets."""
        for child in self.winfo_children():
            child.destroy()

        # use this list to hold refs so we can easily disable later
        self.inputs.clear()
        self.inputs_frame = ttk.Frame(self)
        self.inputs_frame.grid(row=0, column=0, sticky="new")
        # validation command to ensure numeric inputs
        vcmd = self.register(lambda s: s.isnumeric())
        # row 0 ------------------------------------------------------------------------
        lbl = ttk.Label(self.inputs_frame, text="      Devices:")
        lbl.bind("<Button-1>", self.update_devices_list)

        # put the boxes in a frame to make life easier
        ent = ttk.Frame(self.inputs_frame)  # this frame will set the width for the col
        self.device1_entry = ttk.Combobox(
            ent,
            width=15,
            textvariable=self.handler.dev1,
            values=self.devices_list,
            validate="all",
            validatecommand=self.update_devices_list,
        )
        self.device2_entry = ttk.Combobox(
            ent,
            width=15,
            textvariable=self.handler.dev2,
            values=self.devices_list,
            validate="all",
            validatecommand=self.update_devices_list,
        )
        self.device1_entry.grid(row=0, column=0, sticky=tk.W)
        self.device2_entry.grid(row=0, column=1, sticky=tk.E, padx=(4, 0))
        self.inputs.append(self.device1_entry)
        self.inputs.append(self.device2_entry)
        self.render(lbl, ent, 0)

        # row 1 ------------------------------------------------------------------------
        lbl = ttk.Label(self.inputs_frame, text="Project:")
        btn = ttk.Label(
            self.inputs_frame, textvariable=self.handler.project.name, anchor="center"
        )
        self.inputs.append(btn)
        self.render(lbl, btn, 1)

        # row 2 ------------------------------------------------------------------------
        lbl = ttk.Label(self.inputs_frame, text="Test Type:")
        ent = ttk.Frame(self.inputs_frame)
        ent.grid_columnconfigure(0, weight=1)
        ent.grid_columnconfigure(1, weight=1)
        blank_radio = ttk.Radiobutton(
            ent,
            text="Blank",
            variable=self.handler.test.is_blank,
            value=True,
            command=self.update_test_type,
        )
        trial_radio = ttk.Radiobutton(
            ent,
            text="Trial",
            variable=self.handler.test.is_blank,
            value=False,
            command=self.update_test_type,
        )
        blank_radio.grid(row=0, column=0)
        trial_radio.grid(row=0, column=1)
        self.inputs.append(blank_radio)
        self.inputs.append(trial_radio)
        self.render(lbl, ent, 2)

        # row 3 ------------------------------------------------------------------------
        self.grid_rowconfigure(3, weight=1)
        # row 3a is used when the TestHandlerView is in "Blank" mode
        # row 3a -----------------------------------------------------------------------
        self.trial_label_frame = ttk.Frame(self.inputs_frame)

        ttk.Label(self.trial_label_frame, text="Chemical:").grid(
            row=0, column=0, sticky=tk.E, pady=1
        )
        ttk.Label(self.trial_label_frame, text="Rate (ppm):").grid(
            row=1,
            column=0,
            sticky=tk.E,
            pady=1,
        )
        ttk.Label(self.trial_label_frame, text="Clarity:").grid(
            row=2, column=0, sticky=tk.E, pady=1
        )

        self.trial_entry_frame = ttk.Frame(self.inputs_frame)
        self.trial_entry_frame.grid_columnconfigure(0, weight=1)
        chemical_entry = ttk.Entry(
            self.trial_entry_frame, textvariable=self.handler.test.chemical
        )
        chemical_entry.grid(row=0, column=0, sticky="ew", pady=1)
        # validation command to ensure numeric inputs
        vcmd = self.register(lambda s: s.isnumeric())
        rate_entry = ttk.Spinbox(
            self.trial_entry_frame,
            textvariable=self.handler.test.rate,
            from_=0,
            to=999999,
            validate="key",
            validatecommand=(vcmd, "%P"),
        )
        rate_entry.grid(row=1, column=0, sticky="ew", pady=1)
        clarity_entry = ttk.Combobox(
            self.trial_entry_frame,
            values=["Clear", "Slightly hazy", "Hazy"],
            textvariable=self.handler.test.clarity,
        )
        clarity_entry.grid(row=2, column=0, sticky="ew", pady=1)
        clarity_entry.current(0)

        self.inputs.append(chemical_entry)
        self.inputs.append(rate_entry)
        self.inputs.append(clarity_entry)

        # row 3b is used when the TestHandlerView is in "Trial" mode
        # row 3b -----------------------------------------------------------------------
        self.blank_label = ttk.Label(self.inputs_frame, text="Name:")
        self.blank_entry = ttk.Entry(
            self.inputs_frame, textvariable=self.handler.test.name
        )
        self.inputs.append(self.blank_entry)

        # row 4 ------------------------------------------------------------------------
        lbl = ttk.Label(self.inputs_frame, text="Notes:")
        ent = ttk.Entry(self.inputs_frame, textvariable=self.handler.test.notes)
        self.inputs.append(ent)
        self.render(lbl, ent, 4)

        # inputs_frame end -------------------------------------------------------------

        # row 1 ------------------------------------------------------------------------
        ent = ttk.Frame(self)
        self.start_button = ttk.Button(
            ent, text="Start", command=self.handler.start_test
        )
        stop_button = ttk.Button(ent, text="Stop", command=self.handler.request_stop)
        details_button = ttk.Button(
            ent, text="Toggle Details", command=self.update_plot_visible
        )

        self.start_button.grid(row=0, column=0)
        stop_button.grid(row=0, column=1)
        details_button.grid(row=0, column=2)

        ttk.Progressbar(ent, variable=self.handler.progress).grid(
            row=1, columnspan=3, sticky="nwe"
        )
        self.elapsed_label = ttk.Label(ent, textvariable=self.handler.elapsed)
        self.elapsed_label.grid(row=1, column=1)
        ent.grid(row=1, column=0, padx=1, pady=1, sticky="n")
        self.new_button = ttk.Button(ent, text="New", command=self.handler.new_test)

        # rows 0-1 ---------------------------------------------------------------------
        # close all pyplots to prevent memory leak
        plt.close("all")
        self.plot_frame = LivePlot(self, self.handler)
        self.grid_columnconfigure(1, weight=1)  # let it grow
        self.grid_rowconfigure(1, weight=1)

        # row 2 ------------------------------------------------------------------------
        self.log_frame = ttk.Frame(self)
        self.log_text = ScrolledText(
            self.log_frame, background="white", height=5, width=44, state="disabled"
        )
        self.log_text.grid(sticky="ew")

        self.update_test_type()
        self.update_start_button()
        self.update_devices_list()

    # methods to update local state ----------------------------------------------------

    def render(self, label: tk.Widget, entry: tk.Widget, row: int) -> None:
        """Renders a row on the UI. As method for convenience."""
        # pylint: disable=no-self-use
        label.grid(row=row, column=0, sticky=tk.N + tk.E)
        entry.grid(row=row, column=1, sticky=tk.N + tk.E + tk.W, pady=1, padx=1)

    def update_devices_list(self, *args) -> None:
        """Updates the devices list held by the TestHandler."""
        # extra unused args are passed in by tkinter
        def update():
            self.devices_list = sorted([i.device for i in list_ports.comports()])
            if len(self.devices_list) < 1:
                self.devices_list = ["None found"]

            self.device1_entry.configure(values=self.devices_list)
            self.device2_entry.configure(values=self.devices_list)

            if len(self.devices_list) > 1:
                self.device1_entry.current(0)
                self.device2_entry.current(1)

            if not "None found" in self.devices_list:
                LOGGER.debug(
                    "%s found devices: %s", self.handler.name, self.devices_list
                )

        # after here to prevent race conditions
        self.after(1, update)

    def update_input_frame(self, *args) -> None:
        """Disables widgets in the input frame if a Test is running."""
        if self.handler.is_running.get():
            for widget in self.inputs:
                widget.configure(state="disabled")
        else:
            for widget in self.inputs:
                widget.configure(state="normal")

    def update_start_button(self, *args) -> None:
        """Changes the "Start" button to a "New" button when the Test finishes."""
        if self.handler.is_done.get():
            self.start_button.configure(text="New", command=self.handler.new_test)
        else:
            self.start_button.configure(text="Start", command=self.handler.start_test)

    def update_test_type(self, *args):
        """Rebuilds part of the UI to change the entries wrt Test type (blank/trial)."""
        if self.handler.test.is_blank.get():
            self.trial_label_frame.grid_remove()
            self.trial_entry_frame.grid_remove()
            self.render(self.blank_label, self.blank_entry, 3)
            LOGGER.info("%s: changed to Blank mode", self.handler.name)
        else:
            self.blank_label.grid_remove()
            self.blank_entry.grid_remove()
            self.render(self.trial_label_frame, self.trial_entry_frame, 3)
            LOGGER.info("%s: changed to Trial mode", self.handler.name)

    def update_plot_visible(self) -> None:
        """Updates the details view across all TestHandlerViews."""
        is_visible = bool()
        # check if the plot is gridded
        if self.plot_frame.grid_info() != {}:
            is_visible = True

        for tab in self.parent.tabs():
            this = self.parent.nametowidget(tab)
            if not is_visible:  # show the details view
                LOGGER.debug("%s: Showing details view", this.handler.name)
                this.plot_frame.grid(row=0, column=1, rowspan=3)
                this.log_frame.grid(row=2, column=0, sticky="ew")
            else:  # hide the details view
                LOGGER.debug("%s: Hiding details view", this.handler.name)
                this.plot_frame.grid_remove()
                this.log_frame.grid_remove()

    def poll_log_queue(self) -> None:
        """Checks every 100ms if there is a new message in the queue to display."""
        while True:
            try:
                record = self.handler.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.after(100, self.poll_log_queue)

    def display(self, msg: str) -> None:
        """Displays a message in the log."""
        
        self.log_text.configure(state="normal")
        self.log_text.insert(
            tk.END, msg + "\n"
        )  # last arg is for the tag
        self.log_text.configure(state="disabled")
        self.log_text.yview(tk.END)  # scroll to bottom
