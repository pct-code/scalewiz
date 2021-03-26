"""Serial port wrapper for MX-class Teledyne pumps."""

from __future__ import annotations
import logging
from serial import Serial, SerialException, SerialTimeoutException
import time
import typing

from serial.serialutil import PARITY_NONE, STOPBITS_ONE, EIGHTBITS

if typing.TYPE_CHECKING:
    from logging import Logger

import serial

DELAY = 0.1  # 100 ms, recommended by pump docs

class TeledynePump:
    """Serial port wrapper for MX-class Teledyne pumps."""

    def __init__(self, device: str, logger: Logger = None, *args, **kwargs) -> None:
        if logger is None:
            logger = logging.getLogger(logging.getLogger().name + "." + device)
        self.logger = logging.getLogger(logger.name + "." + device)
        self.serial = serial.serial_for_url(
            device,
            baudrate=9600,
            bytesize=EIGHTBITS,
            do_not_open=True,
            parity=PARITY_NONE,
            stopbits=STOPBITS_ONE,
            timeout=0.1, # 100 ms, recommended by pump docs
        )
        # other configuration logic here
        self.open()

    def open(self) -> None:
        """Open the serial port associated with the pump."""
        try:
            self.serial.open()
            self.logger.info("Serial port intitialized")
        except SerialException as e:
            self.logger.critical("Could not open a serial connection")
            self.logger.exception(e)

    def write(self, msg: str) -> str:
        response = ""
        tries = 0
        # SSI documentation recommends 3 attempts
        while not "OK" in response and tries < 3:
            # the pump will look for "\r" as an end-of-command
            self.serial.write((msg + "\r").encode())
            self.logger.debug("Sent %s", msg)
            time.sleep(0.05) # 50 ms 
            response = self.read()
            tries += 1
        return response

    def read(self) -> str:
        response = ""
        tries = 0
        while not "/" in response and tries <3:
            response = self.serial.read_until("/".encode()).decode()
            self.logger.debug("Got response: %s", response)
            tries += 1
        return response

    def run(self) -> None:
        """Run the pump."""
        response = self.write("cc")
        if "OK" in response:
            self.logger.info("Started the pump")
        else:
            self.logger.error("Couldn't start the pump: %s", response)

    def get_pressure(self) -> int:
        """Get the pump's current pressure, or -1 if an error occurs."""
        response = self.write("cc")
        # expect "OK,<pressure>,<flow>/"
        if "OK" in response:
            return int(response.split(",")[1])
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def stop(self) -> None:
        """Stop the pump."""
        response = self.write("st")
        if "OK" in response:
            self.logger.debug("Stopped the pump")
        else:
            self.logger.critical("Could not stop the pump")

    def is_open(self) -> bool:
        return self.serial.is_open

    def close(self) -> None:
        """Close the serial port associated with the pump."""
        self.serial.close()
