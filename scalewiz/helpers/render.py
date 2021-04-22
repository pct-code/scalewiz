"""Grids a label and entry on the passed row."""

from tkinter import ttk


def render(lbl: ttk.Label, ent: ttk.Entry, row: int) -> None:
    """Grids a label and entry on the passed row."""
    lbl.grid(row=row, column=0, sticky="e")
    ent.grid(row=row, column=1, sticky="ew", pady=1)
