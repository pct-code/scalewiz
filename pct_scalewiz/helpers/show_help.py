"""Displays the documentation."""

import logging
import os
import webbrowser

from markdown import markdownFromFile
from markdown.extensions.toc import TocExtension
from pct_scalewiz.helpers.get_resource import get_resource

logger = logging.getLogger("scalewiz")


def show_help() -> None:
    """Displays the documentation in a web browser."""
    logger.info("Opening the help file")
    mdfile = get_resource(r"../../doc/index.md")
    htmlfile = get_resource(r"../../doc/index.html")
    markdownFromFile(
        input=mdfile,
        output=htmlfile,
        extensions=[TocExtension(toc_depth="2-6")],
        encoding="utf8",
    )
    webbrowser.open_new(os.path.abspath(htmlfile))
