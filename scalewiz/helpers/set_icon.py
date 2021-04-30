"""Sets an icon on the current Toplevel."""
from __future__ import annotations

import logging
import os
import tkinter as tk

from scalewiz.helpers.get_resource import get_resource

LOGGER = logging.getLogger("scalewiz")


def set_icon(widget: tk.Widget) -> None:
    """Sets an icon on the current Toplevel."""
    # set the Toplevel's icon
    try:  # this makes me nervous, but whatever
        icon_path = get_resource(r"../components/icon.ico")
    except FileNotFoundError:
        LOGGER.error("Failed to set the icon")

    if os.path.isfile(icon_path):
        widget.winfo_toplevel().wm_iconbitmap(icon_path)
    # for windows, set the taskbar icon
    if os.name == "nt":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("scalewiz")
