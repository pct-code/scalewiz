"""Serial port wrapper for MX-class Teledyne pumps."""


class TeledynePump:
    """Serial port wrapper for MX-class Teledyne pumps."""

    def __init__(self, serialport, logger=None) -> None:
        self.port = serialport
        self.logger = logger

    def run(self) -> None:
        """Run the pump."""
        self.port.write("ru".encode())

    def stop(self) -> None:
        """Stop the pump."""
        self.port.write("st".encode())

    def get_pressure(self) -> int:
        """Get the pump's current pressure."""
        try:
            self.port.write("pr".encode())
            response = self.port.readline().decode()
            psi = response.split(",")[1][:-1]
            return int(psi)
        # pylint: disable=broad-except
        except Exception as error:
            if self.logger is not None:
                self.logger.critical("Reading failed on %s", self.port.port)
                self.logger.exception(error)
            return -1

    def close(self) -> None:
        """Close the serial port associated with the pump."""
        self.port.close()

    def open(self) -> None:
        """Open the serial port associated with the pump."""
        self.port.open()
