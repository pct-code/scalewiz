"""Displays the documentation."""

import logging
import os
import webbrowser

from markdown import markdownFromFile
from markdown.extensions.toc import TocExtension

from scalewiz.helpers.get_resource import get_resource

LOGGER = logging.getLogger("scalewiz")


def show_help() -> None:
    """Displays the documentation in a web browser."""
    LOGGER.info("Opening the docs")
