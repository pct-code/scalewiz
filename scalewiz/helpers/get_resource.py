"""Returns a path to the named resource file, if it exists."""

# this is only really useful for trying to package the app in an exe

import sys
from os import path


def get_resource(name: str) -> str:
    """Returns a path to the passed file name."""
    # only really useful if trying to bundle
    # https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
    path_to_dat = path.abspath(path.join(bundle_dir, name))
    if path.exists(path_to_dat):
        return path_to_dat

    raise FileNotFoundError(f"Could not find a file at {path_to_dat}")
