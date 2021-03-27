"""Serial port wrapper for Next Generation pumps."""

from __future__ import annotations

from typing import Any, Union, TYPE_CHECKING

from pct_scalewiz.models.next_gen_pump_base import (
    LEAK_MODES,
    NextGenPumpBase,
    SOLVENT_COMPRESSIBILITY,
)
from pct_scalewiz.models.pump_error import PumpError

from serial import serial_for_url


class NextGenPump(NextGenPumpBase):
    """Serial port wrapper for Next Generation pumps.
    Commands to the pumps are available as methods on this object.

    Every command will return a dict representing the result of the command.
    This dict will contain at least a "response" key whose value is a string represtation of the pump's response.
    """

    def __init__(self, device: str, *args, **kwargs) -> None:
        """[summary]

        Args:
            device (str): [description]
            logger (Logger, optional): [description]. Defaults to None.
        """
        super().__init__(self, device)

    # general pump commands ------------------------------------------------------------

    def run(self) -> dict[str, str]:
        """Runs the pump.
        """
        return self.command("cc")

    def stop(self) -> dict[str, str]:
        """Stops the pump.
        """
        return self.command("st")

    def keypad_enable(self) -> dict[str, str]:
        """Enables the pump's keypad.
        """
        return self.command("ke")

    def keypad_disable(self) -> dict[str, str]:
        """Disables the pump's keypad.
        """
        return self.command("kd")

    def clear_faults(self) -> dict[str, str]:
        """Clears the pump's faults.
        """
        return self.command("cf")

    def clear_buffer(self) -> dict[str, str]:
        """Clears the pump's command buffer.
        """
        return self.command("#")

    def reset(self) -> dict[str, str]:
        """Resets the pump's user-adjustable values to factory defaults.
        """
        return self.command("re")

    def zero_seal(self) -> dict[str, str]:
        """Zero seal.
        """
        return self.command("zs")

    # bundled info retrieval -- these will return dicts -------------------------------

    def current_conditions(self) -> dict[str, Union[float, int, str]]:
        """Returns a response dict with keys "pressure" and "flowrate".

        Returns:
            dict[str, Union[float, int, str]]: [description]
        """
        result = self.command("cc")
        msg = result["response"].split(",")
        # OK,<pressure>,<flow>/
        result["pressure"] = int(msg[1]),
        result["flowrate"] = float(msg[2][:-1])
        return result

    def current_state(self) -> dict[str, Union[bool, float, int, str]]:
        """[summary]

        Returns:
            dict[str, Union[float, int, str]]: [description]
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
            dict[str, Union[float, int, str]]: [description]
        """
        result = self.command("pi")
        # OK,<flow>,<R/S>,<p_comp>,<head>,0,1,0,0,<UPF>,<LPF>,<prime>,<keypad>,0,0,0,0,<stall>/
        msg = result["response"].split(',')
        result["is running"] = bool(msg[1])
        result["pressure compensation"] = float(msg[3])
        result["head"] = msg[4]
        result["upper limit"] = float(msg[9])
        result["lower limit"] = float(msg[10])
        result["in prime"] = bool(msg[11])
        result["keypad enabled"] = bool(msg[12])
        result["motor stall fault"] = bool(msg[17][:-1])
        return result

    def read_faults(self) -> dict[str, bool]:
        """[summary]

        Returns:
            dict[str, bool]: [description]
        """
        result = self.command("rf")
        msg = result["response"].split(",")
        # OK,<stall>,<UPF>,<LPF>/
        result["motor stall fault"] = bool(msg[1])
        result["upper pressure fault"] = bool(msg(2))
        result["lower pressure fault"] = bool(msg[3][:-1])
        return result

    # general individual property getters ---------------------------------------------

    def get_seal(self) -> dict[str, int]:
        """Gets the seal-life stroke counter as an int."""
        result = self.command("gs")
        # OK,GS:<seal>/
        result["stroke counter"] = int(result["response"].split(":")[1][:-1])
        return result

    def get_user_compensation(self) -> dict[str, float]:
        """Returns the user flowrate compensation as a float representing a percentage.
        Eg. xxx.x = xxx.x%

        Returns:
            Union[int, float]: [description]
        """
        result = self.command("uc")
        # OK,UC:<user_comp>/
        result["user compensation"] = float(result["response"].split(":")[1][:-1])
        return result 

    # general indivdual property setters -----------------------------------------------

    def set_flowrate(self, flowrate: float) -> str:
        """Sets the flowrate of the pump to the passed value,
        not exceeding the pump's maximum.

        Args:
            flowrate (float): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    #  individual properties for pressure enabled pumps --------------------------------

    def get_pressure(self) -> dict[str, float]:
        """Gets the pump's current pressure as a float.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        # OK,<pressure>/
        result = self.command("pr")
        result["pressure"] = float(result["response"].split(",")[:-1])
        return result

    # pressure limits
    # these could get wrapped in @property

    def get_upper_pressure(self) -> dict[str, float]:
        """Gets the pump's current upper pressure limit as an int.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        result = self.command("up")
        # OK,<UPL>/
        result["upper pressure limit"] = int(result["response"].split(",")[:-1])
        return result

    def set_upper_presure(self, int) -> str:
        """Sets the pump's upper pressure limit."""
        raise NotImplementedError

    def get_lower_pressure(self) -> dict[str, float]:
        """Gets the pump's current lower pressure limit as an int.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        result = self.command("lp")
        # OK,<LPL>/
        result["lower pressure limit"] = int(result["response"].split(",")[1][:-1])
        return result

    def set_lower_presure(self, int) -> dict[str, float]:
        """Sets the pump's lower pressure limit."""
        raise NotImplementedError

    # flowrate compensation
    # these could get wrapped in @property

    def get_user_compensation(self) -> dict[str, float]:
        result = self.command("uc")
        # OK,UC:<user_comp>/
        result["user compensation"] = float(result["response"].split(":")[:-1])
        return result

    def set_flowrate_compensation(self, value: float) -> str:
        """Sets the flowrate compensation to a factor between 0.85 and 1.15.
        Passing in a value out of bounds will default to

        Args:
            value (float): [description]
        """
        value = round(value, 2)
        if value < 0.85:
            value = 0.85
        elif value > 1.15:
            value = 1.15
        # pad leading 0s to 4 chars
        # OK,UC:<user_comp>/
        return self.command(
            "uc" + f"{round(value * 100): 04}"
        )
        
    # properties for pumps with a leak sensor ------------------------------------------

    def leak_detected(self) -> dict[str, bool]:
        """Returns a bool representing if a leak is detected.
        Pumps without a leak sensor return False.
        Returns:
            bool: [description]
        """
        result = self.command("ls")
        # OK,LS:<leak>/
        result["leak detected"] = bool(result["response"].split(":")[:-1])
        return result

    def leak_mode(self) -> str:
        """Gets the pump's current leak mode as a string.

        Returns:
            str: A string describing the leak mode.
        """
        result = self.command("lm")
        # OK,LM:<mode>/
        result["leak mode"] = LEAK_MODES.get(int(result["response"].split(":")[:-1]))
        return result

    # properties for pumps with a solvent select feature ------------------------------

    # these could be wrapped in a @property

    def get_solvent(self) -> dict[str, int]:
        """Gets the solvent compressibility value in 10 ** (-6) per bar.

        See NextGenPumpBase.SOLVENT_COMPRESSIBILITY to get the solvent name.

        Returns:
            int: the solvent compressibility value in 10 ** (-6) per bar
        """
        result = self.command("rs")
        result["solvent compressibility"] = int(result["response"].split(",")[1][:-1])
        return result

    def set_solvent(self, value: Union[str, int]) -> str:
        """Sets the solvent compressibility value in 10 ** (-6) per bar.

        Args:
            value (Union[str, int]): The name of a solvent defined in
            SOLVENT_COMPRESSIBILITY, or a compressibility value in
            units of 10 ** (-6) bar.

        Returns:
            str: The pump's response
        """
        # if we got a solvent name string, convert it to an int
        if value in SOLVENT_COMPRESSIBILITY:
            value = SOLVENT_COMPRESSIBILITY.get(value)
        # OK/
        return self.command("ss" + f"{value}")
