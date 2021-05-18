"""Sets an icon on the current Toplevel."""
from __future__ import annotations

import logging
import os
import tkinter as tk
from pathlib import Path

from scalewiz.helpers.get_resource import get_resource

LOGGER = logging.getLogger("scalewiz")


def set_icon(widget: tk.Widget) -> None:
    """Sets an icon on the current Toplevel."""
    # set the Toplevel's icon
    try:  # this makes me nervous, but whatever
        icon_path = Path(get_resource(r"../components/icon.ico")).resolve()
        if icon_path.is_file:
            widget.winfo_toplevel().wm_iconbitmap(icon_path)
        # for windows, set the taskbar icon
        if "nt" in os.name:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("scalewiz")
    except FileNotFoundError:
        LOGGER.error("Failed to set the icon")
