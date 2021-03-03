"""Helper function to spawn a new Toplevel and modify a Project."""

from __future__ import annotations

import logging
import tkinter as tk
import typing
from tkinter import messagebox

from pct_scalewiz.components.project_editor import ProjectEditor

if typing.TYPE_CHECKING:
    from pct_scalewiz.models.test_handler import TestHandler

logger = logging.getLogger("scalwiz")


def modify_project(handler: TestHandler) -> None:
    """Opens a ProjectEditor to modify the current Project."""
    if len(handler.editors) > 0:
        messagebox.showwarning(
            "Project is locked", "Can't modify a Project while it is being accessed"
        )
        return
    window = tk.Toplevel()
    window.protocol("WM_DELETE_WINDOW", lambda: handler.close_editors())
    window.resizable(0, 0)
    handler.editors.append(window)
    editor = ProjectEditor(window, handler)
    editor.grid()
    logger.info(
        "%s: Opened an editor window for %s", handler.name, handler.project.name.get()
    )
