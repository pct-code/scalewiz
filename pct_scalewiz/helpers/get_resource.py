"""Returns a path to the named resource file."""

import sys
from os import path


def get_resource(name: str) -> str:
    """Returns a path to the passed file name."""
    # https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#run-time-information
    bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
    path_to_dat = path.abspath(path.join(bundle_dir, name))
    if path.exists(path_to_dat):
        return path_to_dat
    else:
        raise FileNotFoundError(f"Could not find a file at {path_to_dat}")
