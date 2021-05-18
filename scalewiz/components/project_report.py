"""Editor for Project reporting settings."""

from __future__ import annotations

from tkinter import ttk
from typing import TYPE_CHECKING

from scalewiz.helpers.render import render

if TYPE_CHECKING:
    from scalewiz.models.project import Project


class ProjectReport(ttk.Frame):
    """Editor for Project reporting settings."""

    def __init__(self, parent: ttk.Frame, project: Project) -> None:
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)

        lbl = ttk.Label(self, text="Export format:")
        ent = ttk.Combobox(
            self,
            values=["JSON", "CSV"],
            textvariable=project.output_format,
            state="readonly",
        )
        render(lbl, ent, 0)

        # matplotlib stuff
        # todo implement color selection
        # colorsLbl = ttk.Label(self, text="Plot color cycle:")
        # colorsEnt = ttk.Entry(self)
        # parent.render(colorsLbl, colorsEnt, 1)

        # legendLbl = ttk.Label(self, text="Legend location:")
        # legendEnt = ttk.Combobox(self)
        # parent.render(legendLbl, legendEnt, 2)
