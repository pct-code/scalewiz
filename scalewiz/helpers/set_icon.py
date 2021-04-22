"""Sets an icon on the current Toplevel."""
from __future__ import annotations

import os
import tkinter as tk

from scalewiz.helpers.get_resource import get_resource


def set_icon(widget: tk.Widget):
    """Sets an icon on the current Toplevel."""
    # set the Toplevel's icon
    icon_path = get_resource(
        r"../../assets/chem.ico"
    )  # this makes me nervous, but whatever

    if os.path.exists(icon_path):
        widget.winfo_toplevel().wm_iconbitmap(icon_path)
