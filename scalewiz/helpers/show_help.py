"""Displays the documentation."""

import logging
import webbrowser

LOGGER = logging.getLogger("scalewiz")


def show_help() -> None:
    """Displays the documentation in a web browser."""
    LOGGER.info("Opening the docs")
    webbrowser.open_new("https://github.com/pct-code/scalewiz/blob/main/doc/index.rst")
