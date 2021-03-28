"""Serial port wrapper for MX-class Teledyne pumps."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Union

from serial import SerialException, serial_for_url
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

from pct_scalewiz.models.pump_error import PumpError

if TYPE_CHECKING:
    from logging import Logger


COMMAND_END = "\r".encode()  # terminates messages sent
MESSAGE_END = "/".encode()  # terminates messages received
# these are more or less useful than an int
LEAK_MODES = {
    0: "leak sensor disabled",
    1: "detected leak does not cause fault",
    2: "detected leak does cause fault",
}
# units are 10 ** (-6) per bar
SOLVENT_COMPRESSIBILITY = {
    "acetonitrile": 115,
    "hexane": 167,
    "isopropanol": 84,
    "methanol": 121,
    "tetrahydrofuran": 54,
    "water": 46,
}


class NextGenPumpBase:
    """Serial port wrapper for MX-class Teledyne pumps."""

    def __init__(self, device: str, logger: Logger = None) -> None:
        if logger is None:  # append to the root logger
            logger = logging.getLogger(logging.getLogger().name + "." + device)
        self.logger = logging.getLogger(logger.name + "." + device)
        # fetch a platform-appropriate serial interface
        self.serial = serial_for_url(
            device,
            baudrate=9600,
            bytesize=EIGHTBITS,
            do_not_open=True,
            parity=PARITY_NONE,
            stopbits=STOPBITS_ONE,
            timeout=0.1,  # 100 ms
        )
        # persistent identifying attributes
        self.max_flowrate: float = None
        self.max_pressure: Union[int, float] = None
        self.id: str = None
        self.pressure_units: str = None
        self.head: str = None  # todo
        # other
        self.high_res: bool = None  # 0.00 mL vs 0.000 mL; could rep. as 2 || 3?
        self.flowrate_factor: int = None

        # todo head identification ?
        # other configuration logic here
        self.open()  # open the serial connection
        self.identify()  # populate attributes

    def open(self) -> None:
        """Open the serial port associated with the pump."""
        try:
            self.serial.open()
            self.logger.info("Serial port connected")
        except SerialException as e:
            self.logger.critical("Could not open a serial connection")
            self.logger.exception(e)

    def identify(self):
        """Get persistent pump properties."""
        # general properties ----------------------------------------------------------

        # firmware
        response = self.command("id")  # expect "OK,<ID> Version <ver>/"
        if "OK" in response:
            self.id = response.split(",")[1][:-1]

        # max flowrate
        response = self.command("mf")
        if "OK" in response:  # expect  "OK,MF:<max_flow>/"
            self.max_flowrate = float(response.split(":")[:-1])

        # volumetric resolution - used for setting flowrate
        # expect OK,<flow>,<UPL>,<LPL>,<p_units>,0,<R/S>,0/
        response = self.command("cs")
        flow = len(response.split(",")[1])
        if flow == 4:  # eg. "5.00"
            self.flowrate_factor = 1 * 10 ** (-5)
        elif flow == 5:  # eg. "5.000" -- hopefully
            self.flowrate_factor = 1 * 10 ** (-6)

        # for pumps that have a pressure sensor ---------------------------------------

        # pressure units
        response = self.command("pu")
        if "OK" in response:  # expect "OK,<p_units>/"
            self.pressure_units = response.split(",")[1][:-1]
        # max pressure
        response = self.command("mp")
        if "OK" in response:  # expect "OK,MP:<max_pressure>/"
            self.max_pressure = float(response.split(":")[:-1])

    def command(self, command: bytes) -> dict[str, Any]:
        response = self.write(command)
        if "Er/" in response:
            raise PumpError(
                command=command,
                response=response,
                message="The pump threw an error in response to a command.",
                port=self.serial.name,
                logger=self.logger,
            )
        else:
            return {"response": response}

    def write(self, msg: str, delay=0.015) -> str:
        """Write a command to the pump.A response will be returned after delay seconds.
        Defaults to 0.015 s per pump documentation.

        Returns the pump's response string.
        """
        response = ""
        tries = 0
        # pump docs recommend  3 attempts
        while tries < 3 and "OK" not in response:
            # the pump will look for b"\r" as an end-of-command
            tries += 1
            self.serial.write(msg.encode() + COMMAND_END)
            self.logger.debug("Sent %s (attempt %s/3)", msg, tries)
            time.sleep(delay)
            response = self.read()
        return response

    def read(self) -> str:
        """Reads a single message from the pump."""
        response = ""
        tries = 0
        while tries < 3 and "/" not in response:
            tries += 1
            response = self.serial.read_until(MESSAGE_END).decode()
            self.logger.debug("Got response: %s", response)

        return response

    def close(self) -> None:
        """Closes the serial port associated with the pump."""
        self.serial.close()
        self.logger.info("Serial port closed")

    def is_open(self) -> bool:
        """Returns True if the internal serial port is open."""
        return self.serial.is_open
