"""Editor for Project reporting settings."""

import tkinter as tk
from tkinter import filedialog, ttk

import tkcalendar as tkcal


class ProjectReport(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)
        self.parent = parent

        lbl = ttk.Label(self, text="Export format:")
        ent = ttk.Combobox(
            self,
            values=["JSON", "CSV"],
            textvariable=parent.editorProject.output_format,
        )

        parent.render(lbl, ent, 0)

        # todo implement color selection
        # colorsLbl = ttk.Label(self, text="Plot color cycle:")
        # colorsEnt = ttk.Entry(self)
        # parent.render(colorsLbl, colorsEnt, 1)
        # todo implement legend options
        # legendLbl = ttk.Label(self, text="Legend location:")
        # legendEnt = ttk.Combobox(self)
        # parent.render(legendLbl, legendEnt, 2)

    def loadTemplate(self, *args):
        path = filedialog.askopenfilename(
            initialdir='C:"',
            title="Select report template:",
            filetypes=[("Excel files", "*.xlsx")],
        )

        if not (path == ""):
            self.parent.editorProject.template.set(path)
