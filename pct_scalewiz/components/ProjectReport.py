"""Editor for Project reporting settings."""

import tkinter as tk
from tkinter import ttk, filedialog
import tkcalendar as tkcal

class ProjectReport(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)
        self.parent = parent

        templateLbl = ttk.Label(self, text="Report template:")
        templateEnt = tk.Message(self, textvariable=parent.editorProject.template, aspect=750)
        templateEnt.bind("<Button-1>", self.loadTemplate)
        parent.render(templateLbl, templateEnt, 0)

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
            initialdir="C:\"",
            title="Select report template:",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not (path == ""):
            self.parent.editorProject.template.set(path)








