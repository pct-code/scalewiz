"""Serial port wrapper for Next Generation pumps."""

from __future__ import annotations

import typing
from decimal import Decimal
from typing import Tuple

from serial import SerialException, SerialTimeoutException

from pct_scalewiz.models.teledyne_pump_base import NextGenPumpBase

if typing.TYPE_CHECKING:
    from logging import Logger

from serial import serial_for_url

# todo make these get/sets -> @property


class NextGenPump(NextGenPumpBase):
    """Serial port wrapper for Next Generation pumps."""

    def __init__(self, device: str, logger: Logger = None, *args, **kwargs) -> None:
        super().__init__(self, device, logger)
        self.is_open = lambda: self.serial.is_open # an @property

    # general pump commands

    def run(self) -> None:
        """Runs the pump."""
        response = self.write("cc")
        if "OK" in response:
            self.logger.info("Started the pump")
        else:
            self.logger.error("Couldn't start the pump: %s", response)
        return response

    def stop(self) -> None:
        """Stops the pump."""
        response = self.write("st")
        if "OK" in response:
            self.logger.debug("Stopped the pump")
        else:
            self.logger.critical("Could not stop the pump")

    # bundled info retrieval 
    
    def current_conditions(self) -> Tuple[int, float]:
        """Gets the current pressure and flowrate as a tuple.
        Returns -1 if an error occurs."""
        response = self.write("cc")
        if "OK" in response:  # expect "OK,<pressure>,<flow>/"
            return int(response.split(",")[1]), float(response.split(",")[2][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1
    
    def current_state(self) -> Tuple[float, float, float, str, int,]:
        """Returns the flowrate, upper pressure limit, lower pressure limit,
        pressure units, and running state as a tuple.
        Returns -1 if an error occurs.
        """
        response = self.write("cs")
        # expect OK,<flow>,<UPL>,<LPL>,<p_units>,0,<R/S>,0/
        if "OK" in response:  
            msg = response.split(",")
            return (
                float(msg[1]),
                float(msg[2]),
                float(msg[3]),
                msg[4],
                int(msg[6]),
            )
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1
    
    def read_faults(self):
        raise NotImplementedError

    # individual property getters

    def get_max_flowrate(self) -> float:
        """Gets the maximum flowrate as a float. Returns -1 if an error occurs."""
        response = self.write("mf")
        if "OK" in response:  # expect "OK,MF:<max_flow>/"
            return float(response.split(":")[0][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def get_seal(self) -> int:
        """Gets the seal-life stroke counter as an int.
        Returns -1 if an error occurs."""
        raise NotImplementedError
    
    # indivdual property setters

    def set_flowrate(self, flowrate: float) -> None:
        """Sets the flowrate of the pump to the passed value,
        not exceeding the pump's maximum."""
        raise NotImplementedError
    
    # keypad disable/enable, user_comp, #

    #  individual properties for pressure enabled pumps

    def get_pressure(self) -> int:
        """Gets the pump's current pressure as an int. Returns -1 if an error occurs."""
        # todo deal with bar/MPa responses
        response = self.write("pr")
        if "OK" in response:  # expect "OK,<pressure>/"
            return int(response.split(",")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def get_maximum_pressure(self) -> int:
        """Gets the pump's maximum pressure limit as an int.
        Returns. -1 if an error occurs."""
        # todo deal with bar/MPa responses
        response = self.write("mp")
        if "OK" in response:  # expect "OK,<UPL>/"
            return int(response.split(",")[1][:-1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

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

    def set_upper_presure(self, int) -> None:
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

    def set_lower_presure(self, int) -> None:
        """Sets the pump's lower pressure limit."""
        raise NotImplementedError
