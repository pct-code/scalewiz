"""Editor for Project reporting settings."""

from tkinter import ttk


class ProjectReport(ttk.Frame):
    """Editor for Project reporting settings."""

    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self.grid_columnconfigure(1, weight=1)
        self.parent = parent

        lbl = ttk.Label(self, text="Export format:")
        ent = ttk.Combobox(
            self,
            values=["JSON", "CSV"],
            textvariable=parent.editor_project.output_format,
        )

        parent.render(lbl, ent, 0)

        # matplotlib stuff
        # todo implement color selection
        # colorsLbl = ttk.Label(self, text="Plot color cycle:")
        # colorsEnt = ttk.Entry(self)
        # parent.render(colorsLbl, colorsEnt, 1)

        # todo implement legend options
        # legendLbl = ttk.Label(self, text="Legend location:")
        # legendEnt = ttk.Combobox(self)
        # parent.render(legendLbl, legendEnt, 2)
