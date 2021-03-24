"""Serial port wrapper for MX-class Teledyne pumps."""

from __future__ import annotations
import logging
from serial import Serial, SerialException, SerialTimeoutException
import time
import typing

if typing.TYPE_CHECKING:
    from logging import Logger

import serial

DELAY = 0.001  # 100 ms, recommended by pump docs

class TeledynePump:
    """Serial port wrapper for MX-class Teledyne pumps."""

    def __init__(self, device: str, logger: Logger = None, *args, **kwargs) -> None:
        if logger is None:
            logger = logging.getLogger(logging.getLogger().name + "." + device)
        
        self.logger = logging.getLogger(logger.name + "." + device)
        self.serial = serial.serial_for_url(
            port=device, timeout=DELAY, do_not_open=True
        )

        self.open()

    def open(self) -> None:
        """Open the serial port associated with the pump."""
        try:
            self.serial.open()
        except SerialException as e:
            self.logger.critical("Could not open a serial connection")
            self.logger.exception(e)

    def write(self, msg: str):
        # the pump will look for "\r" as an end
        self.serial.write("{}\r".format(msg).encode())
        self.logger.debug("Sent %s", msg)

    def read(self, delay = True) -> str:
        self.logger.debug("Reading...")
        if delay:
            time.sleep(DELAY)
        response = self.serial.read_until("/")
        self.logger.debug(response)
        return response 

    def run(self) -> None:
        """Run the pump."""
        self.write("ru")

    def get_pressure(self) -> int:
        """Get the pump's current pressure."""
        self.write("cc")
        response = self.read()
        # expect OK,<pressure>,<flow>/
        if "OK" in response:
            return response.split(",")[0]
        else:
            self.logger.error("Unexpected response: %s", response)
            return -1

    def stop(self) -> None:
        """Stop the pump."""
        self.write("st")
        response = self.read()
        if "OK" in response:
            self.logger.debug("Stopped the pump")
        else:
            self.logger.critical("Could not stop the pump")

    def close(self) -> None:
        """Close the serial port associated with the pump."""
        self.serial.close()
