"""Serial port wrapper for Next Generation pumps."""

from __future__ import annotations
from logging import Logger
from tkinter.constants import NONE

from typing import TYPE_CHECKING, Any, Union

from serial import serial_for_url

from pct_scalewiz.models.next_gen_pump_base import (
    LEAK_MODES,
    SOLVENT_COMPRESSIBILITY,
    NextGenPumpBase,
)
from pct_scalewiz.models.pump_error import PumpError


class NextGenPump(NextGenPumpBase):
    """Serial port wrapper for Next Generation pumps.
    Commands to the pumps are available as methods on this object.

    Every command will return a dict representing the result of the command.
    This dict will contain at least a "response" key whose value is a string represtation of the pump's response.
    """

    def __init__(self, device: str, logger: Logger = None) -> None:
        """[summary]

        Args:
            device (str): [description]
            logger (Logger, optional): [description]. Defaults to None.
        """
        super().__init__(device, logger)

    # general pump commands ------------------------------------------------------------

    def run(self) -> None:
        """Runs the pump. 🏃‍♀️"""
        return self.command("ru")

    def stop(self) -> None:
        """Stops the pump. 🛑 """
        self.command("st")

    def keypad_enable(self) -> None:
        """Enables the pump's keypad. 🔓"""
        self.command("ke")

    def keypad_disable(self) -> None:
        """Disables the pump's keypad. 🔒"""
        self.command("kd")

    def clear_faults(self) -> None:
        """Clears the pump's faults. 😇"""
        self.command("cf")

    def reset(self) -> None:
        """Resets the pump's user-adjustable values to factory defaults. ✨"""
        self.command("re")

    def zero_seal(self) -> None:
        """Zero the seal-life stroke counter."""
        self.command("zs")

    # bundled info retrieval -- these will return dicts -------------------------------
    # all dicts have a "response" key whose value is the pump's decoded response string

    def current_conditions(self) -> dict[str, Union[float, str]]:
        """Returns a dictionary describing the current conditions of the pump.

        Returns:
            dict[str, Union[float, int, str]]: keys "pressure", "flowrate", "response"
        """
        result = self.command("cc")
        msg = result["response"].split(",")
        # OK,<pressure>,<flow>/
        result["pressure"] = (float(msg[1]),)
        result["flowrate"] = float(msg[2][:-1])
        return result

    def current_state(self) -> dict[str, Union[bool, float, int, str]]:
        """Returns a dictionary describing the current state of the pump.

        Returns:
            dict[str, Union[bool, float, str]]: keys "flowrate", "upper limit",
            "lower limit", "pressure units", "is running", "response"
        """
        result = self.command("cs")
        # OK,<flow>,<UPL>,<LPL>,<p_units>,0,<R/S>,0/
        msg = result["response"].split(",")
        result["flowrate"] = float(msg[1])
        result["upper limit"] = float(msg[2])
        result["lower limit"] = float(msg[3])
        result["pressure units"] = msg[4]
        result["is running"] = bool(msg[6])
        return result

    def pump_information(self) -> dict[str, Union[float, int, str]]:
        """Gets a dictionary of information about the pump.

        Returns:
            dict[str, Union[float, int, str]]: "flowrate", "is running",
            "pressure compensation", "head", "upper limit", "lower limit", "in prime",
            "keypad enabled", "motor stall fault", "response"
        """
        result = self.command("pi")
        # OK,<flow>,<R/S>,<p_comp>,<head>,0,1,0,0,
        # <UPF>,<LPF>,<prime>,<keypad>,0,0,0,0,<stall>/
        msg = result["response"].split(",")
        result["flowrate"] = bool(msg[1])
        result["is running"] = bool(msg[2])
        result["pressure compensation"] = float(msg[3])
        result["head"] = msg[4]
        result["upper limit"] = float(msg[9])
        result["lower limit"] = float(msg[10])
        result["in prime"] = bool(msg[11])
        result["keypad enabled"] = bool(msg[12])
        result["motor stall fault"] = bool(msg[17][:-1])
        return result

    def read_faults(self) -> dict[str, bool]:
        """Returns a dictionary representing the pump's fault status.

        Returns:
            dict[str, bool]: "motor stall fault", "upper pressure fault",
            "lower pressure fault", "reponse"
        """
        result = self.command("rf")
        msg = result["response"].split(",")
        # OK,<stall>,<UPF>,<LPF>/
        result["motor stall fault"] = bool(msg[1])
        result["upper pressure fault"] = bool(msg(2))
        result["lower pressure fault"] = bool(msg[3][:-1])
        return result

    # general properties  ---------------------------------------------

    def get_stroke_counter(self) -> int:
        """Gets the seal-life stroke counter as an int."""
        result = self.command("gs")
        # OK,GS:<seal>/
        return int(result["response"].split(":")[1][:-1])

    # flowrate compensation
    # these could get wrapped in @property
    def get_flowrate_compensation(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        result = self.command("uc")
        # OK,UC:<user_comp>/
        return float(result["response"].split(":")[1][:-1]) / 100

    def set_flowrate_compensation(self, value: float) -> None:
        """Sets the flowrate compensation to a factor between 0.85 and 1.15.
        Passing in a value out of bounds will default to the nearest bound.

        Args:
            value (float): [description]
        """
        value = round(value, 2)
        if value < 0.85:
            value = 0.85
        elif value > 1.15:
            value = 1.15
        # pad leading 0s to 4 chars
        # eg. 0.85 -> 850 ->  UC0850
        # OK,UC:<user_comp>/
        self.command("uc" + f"{round(value * 1000):04}")

    def set_flowrate(self, flowrate: float) -> None:
        """Sets the flowrate of the pump to the passed value,
        not exceeding the pump's maximum.

        Args:
            flowrate (float): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    #  individual properties for pressure enabled pumps --------------------------------

    def get_pressure(self, unit: str = None) -> float:
        """Gets the pump's current pressure as a float using the pump's pressure units.
        Pressure units are most easily found on a pump instance at .pressure_units
        """
        result = self.command("pr")
        # OK,<pressure>/
        return float(result["response"].split(",")[1][:-1])

    # pressure limits
    # these could get wrapped in @property
    def get_upper_pressure(self) -> float:
        """Gets the pump's current upper pressure limit as a float."""
        result = self.command("up")
        # OK,<UPL>/
        return float(result["response"].split(",")[1][:-1])

    def set_upper_presure(self, limit: float) -> None:
        """Sets the pump's upper pressure limit."""
        raise NotImplementedError

    def get_lower_pressure(self) -> float:
        """Gets the pump's current lower pressure limit as an int.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        result = self.command("lp")
        # OK,<LPL>/
        result["lower pressure limit"] = int(result["response"].split(",")[1][:-1])
        return result

    def set_lower_presure(self, limit: float) -> None:
        """Sets the pump's lower pressure limit."""
        raise NotImplementedError

    # properties for pumps with a leak sensor ------------------------------------------

    def leak_detected(self) -> bool:
        """Returns a bool representing if a leak is detected.
        Pumps without a leak sensor always return False.
        Returns:
            bool: [description]
        """
        result = self.command("ls")
        # OK,LS:<leak>/
        return bool(result["response"].split(":")[1][:-1])

    def leak_mode(self) -> int:
        """Gets the pump's current leak mode as an int.

        Returns:
            int: 0 if disabled. 1 if detected leak will fault. 2 if it will not fault.
        """
        result = self.command("lm")
        # OK,LM:<mode>/
        mode = int(result["response"].split(":")[1][:-1])
        # could return a descriptive string instead with the following line
        # return LEAK_MODES.get(mode)
        return mode

    # properties for pumps with a solvent select feature ------------------------------
    # these could be wrapped in a @property
    def get_solvent(self) -> int:
        """Gets the solvent compressibility value in 10 ** (-6) per bar.
        See NextGenPumpBase.SOLVENT_COMPRESSIBILITY to get the solvent name.

        Returns:
            int: the solvent compressibility value in 10 ** (-6) per bar
        """
        result = self.command("rs")
        # OK,<solvent>/
        return int(result["response"].split(",")[1][:-1])

    def set_solvent(self, value: Union[str, int]) -> None:
        """Sets the solvent compressibility value in 10 ** (-6) per bar.
        Alternatively, accepts the name of a solvent as mapped in SOLVENT_COMPRESSIBILITY.

        Args:
            value (Union[str, int]): The name of a solvent defined in
            SOLVENT_COMPRESSIBILITY, or a compressibility value in
            units of 10 ** (-6) bar.
        """
        # if we got a solvent name string, convert it to an int
        if value in SOLVENT_COMPRESSIBILITY.keys():
            value = SOLVENT_COMPRESSIBILITY.get(value)
        # OK/
        self.command("ss" + f"{value}")
