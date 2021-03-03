"""Helper function to spawn a Toplevel for evaluating a Project."""

from __future__ import annotations

import logging
import tkinter as tk
import typing
from tkinter import messagebox

from pct_scalewiz.components.evaluation_frame import EvaluationFrame

if typing.TYPE_CHECKING:
    from pct_scalewiz.models.test_handler import TestHandler

logger = logging.getLogger("scalwiz")


def evaluate_project(handler: TestHandler) -> None:
    """Opens a Toplevel with an Evaluation Frame for current Project."""
    if len(handler.editors) > 0:
        messagebox.showwarning(
            "Project is locked", "Can't modify a Project while it's being accessed"
        )
        return
    window = tk.Toplevel()
    window.protocol("WM_DELETE_WINDOW", lambda: handler.close_editors())
    window.resizable(0, 0)
    # todo #16 try passing in the editor itself.
    # then can rebuild it or winfo_toplevel.destroy()
    handler.editors.append(window)
    editor = EvaluationFrame(window, handler)
    editor.grid()
    logger.info(
        "%s: Opened an evaluation window for %s",
        handler.name,
        handler.project.name.get(),
    )
