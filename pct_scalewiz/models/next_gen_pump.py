"""Serial port wrapper for Next Generation pumps."""

from __future__ import annotations

import typing
from typing import Union

from pct_scalewiz.models.next_gen_pump_base import LEAK_MODES, NextGenPumpBase, SOLVENT_COMPRESSIBILITY

if typing.TYPE_CHECKING:
    from logging import Logger

from serial import serial_for_url


class NextGenPump(NextGenPumpBase):
    """Serial port wrapper for Next Generation pumps."""

    def __init__(self, device: str, logger: Logger = None, *args, **kwargs) -> None:
        """[summary]

        Args:
            device (str): [description]
            logger (Logger, optional): [description]. Defaults to None.
        """
        super().__init__(self, device, logger)

    # general pump commands -- these return "OK/" or "Er/" ----------------------------

    def run(self) -> str:
        """Runs the pump.

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("cc")
        if "OK" in response:
            self.logger.info("Started the pump")
        else:
            self.logger.critical("Couldn't start the pump: %s", response)
        return response

    def stop(self) -> str:
        """Stops the pump.

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("st")
        if "OK" in response:
            self.logger.info("Stopped the pump")
        else:
            self.logger.critical("Could not stop the pump")
        return response

    def keypad_enable(self) -> str:
        """Enables the pump's keypad.

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("ke")
        if "OK" in response:
            self.logger.info("Enabled the keypad")
        else:
            self.logger.error("Could not enable the keypad")
        return response

    def keypad_disable(self) -> str:
        """Disables the pump's keypad.

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("kd")
        if "OK" in response:
            self.logger.info("Disabled the keypad")
        else:
            self.logger.error("Could not disable the keypad")
        return response

    def clear_faults(self)  -> str:
        """Clears the pump's faults.

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("cf")
        if "OK" in response:
            self.logger.info("Cleared pump faults")
        else:
            self.logger.error("Couldn't clear pump faults")
        return response
    
    def clear_buffer(self) -> None:
        """Clears the pump's command buffer."""
        self.write("#")
    
    def reset(self) -> str:
        """Resets the pump's user-adjustable values to factory defaults.

        Returns:
            str: "OK/" || "Er/"
        """
        response =self.write("re")
        if "OK" in response:
            self.logger.info("Reset all user-adjustable values to factory defaults")
        else:
            self.logger.error("Could not reset the pump")
        return response

    def zero_seal(self) -> str:
        """[summary]

        Returns:
            str: "OK/" || "Er/"
        """
        response = self.write("zs")
        if "OK" in response:
            self.logger.info("Reset the seal-life stroke counter to 0")
        else:
            self.logger.error("Could not reset seal-life stroke counter")
        return response

    # bundled info retrieval -- these will return dicts -------------------------------

    def current_conditions(self) -> dict[str, Union[float, int, str]]:
        """[summary]

        Returns:
            dict[str, Union[float, int, str]]: [description]
        """
        response = self.write("cc")
        if "OK" in response:  # expect "OK,<pressure>,<flow>/"
            return {
                "response": response,
                "pressure": int(response.split(",")[1]),
                "flowrate": float(response.split(",")[2][:-1]),
            }
        else:
            self.logger.error("Unexpected response: %s", response)
            return {"response": response}

    def current_state(self) -> dict[str, Union[bool, float, int, str]]:
        """[summary]

        Returns:
            dict[str, Union[float, int, str]]: [description]
        """
        response = self.write("cs")
        # expect OK,<flow>,<UPL>,<LPL>,<p_units>,0,<R/S>,0/
        if "OK" in response:
            msg = response.split(",")
            return {
                "response": response,
                "flowrate": float(msg[1]),
                "upper limit": float(msg[2]),
                "lower limit": float(msg[3]),
                "pressure units": msg[4],
                "is running": bool(msg[6]),
            }
        else:
            self.logger.error("Unexpected response: %s", response)
            return {"response": response}

    def pump_information(self) -> dict[str, Union[float, int, str]]:
        """Gets a dictionary of information about the pump.

        Returns:
            dict[str, Union[float, int, str]]: [description]
        """
        response = self.write("pi")
        if "OK" in response:
            msg = response.split(",")
            return {
                "response": response,
                "is running": bool(msg[1]),
                "pressure compensation": float(msg[3]),
                "head": msg[4],
                "upper limit": float(msg[9]),
                "lower limit": float(msg[10]),
                "in prime": bool(msg[11]),
                "keypad enabled": bool(msg[12]),
                "motor stall fault": bool(msg[17][:-1]),
            }
        else:
            return {"response": response}

    def read_faults(self) -> dict[str, bool]:
        """[summary]

        Returns:
            dict[str, bool]: [description]
        """
        response = self.write("rf")
        if "OK" in response:  # expect "OK,<stall>,<UPF>,<LPF>/"
            msg = response.split(",")
            return {
                "response": response,
                "motor stall fault": bool(msg[1]),
                "upper pressure fault": bool(msg(2)),
                "lower pressure fault": bool(msg[3]),
            }
        else:
            return {"response": response}
    
    # general individual property getters ---------------------------------------------

    def get_seal(self) -> int:
        """Gets the seal-life stroke counter as an int.
        Returns -1 if an error occurs."""
        response = self.write("gs")
        if "OK" in response:  # expect "OK,GS:<seal>/"
            return int(response.split(":")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1
    
    def get_user_compensation(self) -> Union[int, float]:
        """Returns the user flowrate compensation as a float representing a percentage.
        Eg. xxx.x = xxx.x%

        Returns:
            Union[int, float]: [description]
        """
        response = self.write("uc")
        if "OK" in response:
            return float(response.split(":")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    # general indivdual property setters -----------------------------------------------

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

    def get_pressure(self) -> float:
        """Gets the pump's current pressure as a float.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        response = self.write("pr")
        if "OK" in response:  # expect "OK,<pressure>/"
            return int(response.split(",")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    # these could get wrapped with @property
    
    def get_upper_pressure(self) -> int:
        """Gets the pump's current upper pressure limit as an int.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        response = self.write("up")
        if "OK" in response:  # expect "OK,<UPL>/"
            return int(response.split(",")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def set_upper_presure(self, int) -> str:
        """Sets the pump's upper pressure limit."""
        raise NotImplementedError

    def get_lower_pressure(self) -> int:
        """Gets the pump's current lower pressure limit as an int.
        Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        response = self.write("lp")
        if "OK" in response:  # expect "OK,<UPL>/"
            return int(response.split(",")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def set_lower_presure(self, int) -> str:
        """Sets the pump's lower pressure limit."""
        raise NotImplementedError
    
    def get_user_compensation(self) -> float:
        response = self.write("uc")
        if "OK" in response: # expect "OK,UC:<user_comp>/"
            compensation = float(response.split(":")[:-1]) 
            self.logger.info("Current flowrate compensation is %s", compensation)
        else:
            self.logger.error("Unexpected response: %s", response)


    def set_user_compensation(self, float) -> None:
        """[summary]

        Args:
            float ([type]): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    # properties for pumps with a leak sensor ------------------------------------------

    def leak_detected(self) -> Union[bool, None]:
        """Returns a bool representing if a leak is detected,
        or None if there's no sensor.

        Returns:
            Union[bool, None]: [description]
        """
        response = self.write("ls")
        if "OK" in response: # expect "OK,LS:<leak>/"
            return bool(response.split(":")[:-1])
        else:
            return None

    def leak_mode(self) -> str:
        """Gets the pump's current leak mode as a string.

        Returns:
            str: A string describing the leak mode.
        """
        response = self.write("lm")
        if "OK" in response: # expect "OK,LM:<mode>/"
            mode = LEAK_MODES.get(int(response.split(":")[:-1]))
            self.logger.info("The leak mode is %s", mode)
            return mode
        else:
            self.logger.error("Unexpected response: %s", response)
            return str(None)
    
    # properties for pumps with a solvent select feature ------------------------------

    # these could be wrapped in a @property

    def get_solvent(self) -> int:
        """Gets the solvent compressibility value in 10 ** (-6) per bar.

        See NextGenPumpBase.SOLVENT_COMPRESSIBILITY to get the solvent name.

        Returns:
            int: the solvent compressibility value in 10 ** (-6) per bar
        """
        response = self.write("rs")
        if "OK" in response: # expect "OK,<solvent>/"
            compressibility = int(response.split(",")[1][:-1])
            self.logger.info(
                "The current solvent compressibility is %s",
                compressibility
                )
            return compressibility
    
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
        # send the command
        response = self.write("ss" + f"{value}")
        if "OK" in response:
            self.logger.info("Set the solvent compressibility to %s", value)
        else:
            self.logger.error("Couldn't set the solvent compressibility to %s", value)
        return response