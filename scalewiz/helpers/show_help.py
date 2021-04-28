"""Displays the documentation."""

import logging
import webbrowser

from scalewiz.helpers.get_resource import get_resource

LOGGER = logging.getLogger("scalewiz")


def show_help() -> None:
    """Displays the documentation in a web browser."""
    LOGGER.info("Opening the docs")
    webbrowser.open_new("https://github.com/teauxfu/scalewiz/blob/main/doc/index.rst")
