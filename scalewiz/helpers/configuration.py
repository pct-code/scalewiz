"""This module defines functions that deal with program configuration."""

# todo color cycle for reports

from __future__ import annotations

import os
from logging import getLogger
from pathlib import Path
from typing import Union

from appdirs import user_config_dir
from tomlkit import comment, document, dumps, loads, nl, table

LOGGER = getLogger("scalewiz.config")

CONFIG_DIR = Path(user_config_dir("ScaleWiz", "teauxfu"))
CONFIG_FILE = Path(os.path.join(CONFIG_DIR, "config.toml"))


def ensure_config() -> None:
    """Makes a config directory if one doesn't exist.

    Args:
        directory (str): path for the config directory
    """
    # make sure we have a place to store data
    if not CONFIG_DIR.is_dir():
        LOGGER.info("No config directory found. Making one now at %s", CONFIG_DIR)
        CONFIG_DIR.mkdir(parents=True)
    # make sure the file exists and isn's empty
    if not CONFIG_FILE.is_file() or os.stat(CONFIG_FILE).st_size == 0:
        LOGGER.info(
            "No config file found in %s. Making one now at %s", CONFIG_DIR, CONFIG_FILE
        )
        init_config()
    # todo #19 make sure the config isn't missing keys


def init_config():
    """Ensures a user config dir and file."""
    doc = generate_default()
    # write to file
    with CONFIG_FILE.open("w") as file:
        file.write(dumps(doc))
    # report
    if CONFIG_FILE.is_file():
        LOGGER.info("Successfully built a new config file at %s", CONFIG_FILE)
    else:
        LOGGER.warning("Failed to init a config file at %s", CONFIG_FILE)


def generate_default() -> document:
    """Generates the default TOML doc."""
    # make the toml
    doc = document()
    # orient the user
    doc.add("This is the configuration file for ScaleWiz")
    doc.add(
        comment(
            "This is a TOML document, "
            "made according to the spec at https://toml.io/en/"
        )
    )
    doc.add(
        comment(
            "If it behaves unexpectedly, try using "
            "https://www.toml-lint.com/ to check your edits"
        )
    )
    doc.add(
        comment(
            "You may delete this file to generate a new one "
            "the next time you run ScaleWiz"
        )
    )
    doc.add(
        comment(
            "If valid TOML is behaving unexpectedly in ScaleWiz, "
            "please open an issue at https://github.com/teauxfu/scalewiz/issues"
        )
    )

    # these will get updated between user sessions
    recents = table()
    recents["analyst"] = "teauxfu"
    recents["project"] = ""
    doc["recents"] = recents
    doc["recents"].comment("these will get updated between user sessions")

    # general defaults
    params = table()

    params["baseline"] = 0
    params["baseline"].comment("psi, an integer > 0")

    params["flowrate"] = 1.0
    params["flowrate"].comment("mL/min, a float > 0.0")

    params["output_format"] = "CSV"
    params["output_format"].comment('choose from ("CSV", "JSON")')

    params["pressure_limit"] = 1
    params["pressure_limit"].comment("psi, an integer > 0")

    params["reading_interval"] = 1.0
    params["reading_interval"].comment("seconds between readings, a float > 0.0")

    params["test_temperature"] = 1.0
    params["test_temperature"].comment("test temperature in °F, > 0.0")

    params["time_limit"] = 1.0
    params["time_limit"].comment("minutes, a float > 0.0")

    params["uptake_time"] = 1.0
    params["uptake_time"].comment(
        "seconds between pumps starting and data collection, a float => 0.0"
    )

    doc["defaults"] = params
    doc["defaults"].comment("these will get used when making new projects")
    # all done
    return doc


def open_config() -> None:
    """Opens the config file."""
    ensure_config()
    if CONFIG_FILE.is_file():
        os.startfile(CONFIG_FILE)


def get_config() -> dict[str, Union[float, int, str]]:
    """Returns the current configuration as a dict."""
    ensure_config()
    with CONFIG_FILE.open("r") as file:
        defaults = loads(file.read())
    return defaults


def update_config(table: str, key: str, value: Union[float, int, str]):
    """Update the config with the passed values.

    Args:
        table (str): table to update (expects "recents" or "defaults")
        key (str): the key to update
        value (Union[float, int, str]): the new value of `key`
    """
    ensure_config()
    doc = loads(CONFIG_FILE.open("r").read())
    if table in doc.keys() and key in doc[table].keys():
        doc[table][key] = value
        CONFIG_FILE.write_text(dumps(doc))
        LOGGER.info("Updated %s.%s to %s", table, key, value)
    else:
        LOGGER.info("Failed to update %s.%s to %s", table, key, value)
