"""Serial port wrapper for MX-class Teledyne pumps."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Union

from serial import SerialException, serial_for_url
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

if TYPE_CHECKING:
    from logging import Logger


COMMAND_END = "\r".encode() # terminates messages sent
MESSAGE_END = "/".encode() # terminates messages received


class NextGenPumpBase:
    """Serial port wrapper for MX-class Teledyne pumps."""

    def __init__(self, device: str, logger: Logger = None) -> None:
        if logger is None: # append to the root logger
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
        self.high_res: bool = None  # 0.00 mL vs 0.000 mL; could rep. as 2 || 3?
        self.flowrate_factor: int = None
        self.max_flowrate: Union[int, float] = None
        self.part_number: int = None
        self.firmware_version: str = None
        self.pressure_units: str = None
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
        # firmware
        response = self.write("id")  # expect OK, <ID> Version <ver>/
        self.part_number = int(response.split(",")[1].split("Version")[0])
        self.firmware_version = response.split("Version")[1][:-1]
        # volumetric resolution - used for setting flowrate
        response = self.write("cs")  # expect OK,<flow>,<UPL>,<LPL>,<p_units>,0,<R/S>,0/
        flow = len(response.split(",")[1])
        if flow == 4:  # eg. "5.00"
            self.flowrate_factor = 1 * 10 ** (-5)
        else:  # eg. "5.000" -- hopefully
            self.flowrate_factor = 1 * 10 ** (-6)
        # pressure units, if we have a sensor
        response = self.write("pu")
        if "OK" in response:  # expect "OK,<p_units>/"
            self.pressure_units = response.split(",")[1][:-1]

    def write(self, msg: str, delay=0.015) -> str:
        """Write a command to the pump.A response will be returned after delay seconds.
        Defaults to 0.015 s per pump documentation.
        """
        response = ""
        tries = 0
        # pump docs recommend  3 attempts
        while tries < 3 and "OK" not in response:
            # the pump will look for "\r" as an end-of-command
            tries += 1
            self.serial.write((msg).encode() + COMMAND_END)
            self.logger.debug("Sent %s", msg)
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

