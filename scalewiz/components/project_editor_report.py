"""Editor for Project reporting settings."""

from __future__ import annotations

from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scalewiz.components.project_editor import ProjectWindow
    from scalewiz.models.project import Project


def render(lbl: ttk.Label, ent: ttk.Entry, row: int) -> None:
    """Grids a label and entry on the passed row."""
    lbl.grid(row=row, column=0, sticky="e")
    ent.grid(row=row, column=1, sticky="ew", pady=1)


class ProjectReport(ttk.Frame):
    """Editor for Project reporting settings."""

    def __init__(self, parent: ProjectWindow, project: Project) -> None:
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

        lbl = ttk.Label(self, text="Default pump:")
        ent = ttk.Combobox(
            self,
            values=["Pump 1", "Pump 2", "Average"],
            textvariable=project.default_pump,
            state="readonly",
        )
        render(lbl, ent, 1)

        # matplotlib stuff
        # colorsLbl = ttk.Label(self, text="Plot color cycle:")
        # colorsEnt = ttk.Entry(self)
        # parent.render(colorsLbl, colorsEnt, 1)

        # legendLbl = ttk.Label(self, text="Legend location:")
        # legendEnt = ttk.Combobox(self)
        # parent.render(legendLbl, legendEnt, 2)
