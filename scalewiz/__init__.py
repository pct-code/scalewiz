"""The parent module for the scalewiz package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tinydb import TinyDB

if TYPE_CHECKING:
    from tkinter import Tk

from scalewiz.helpers.configuration import get_config

ROOT: Tk = None
CONFIG: dict = get_config()
DATABASE: TinyDB = TinyDB(CONFIG["recents"]["database"])
