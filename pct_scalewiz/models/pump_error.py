from logging import Logger


class PumpError(Exception):
    """Raised when the pump responds with the error code "Er/"."""

    def __init__(
        self,
        command: str,
        response: str,
        message: str,
        port: str,
    ) -> None:
        """Raised when the pump responds with the error code "Er/".

        Args:
            command (str): The command that resulted in an error.
            response (str): The pump's response to the error.
            message (str): Message to display with the error.
            port (str): Serial port the error occurred on.
        """
        super().__init__(self, message)
        self.command: str = command
        self.response: str = response
        self.port: str = port
