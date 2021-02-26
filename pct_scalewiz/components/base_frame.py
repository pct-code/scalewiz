"""A base frame class to be used by most of the other UI elements."""

import sys
import tkinter as tk
from os import path
from tkinter import ttk

from pct_scalewiz.helpers.get_resource import get_resource


class BaseFrame(ttk.Frame):
    """A base frame class to be used by most of the other UI elements."""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        # set the Toplevel's icon
        icon_path = get_resource(
            r"../../assets/chem.ico"
        )  # this makes me nervous, but whatever

        if path.isfile(icon_path):
            self.winfo_toplevel().wm_iconbitmap(icon_path)
            print(self.winfo_toplevel().wm_iconbitmap())
