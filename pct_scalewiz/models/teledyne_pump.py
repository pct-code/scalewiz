"""Serial port wrapper for MX-class Teledyne pumps."""


class TeledynePump:
    def __init__(self, serialport, logger=None):
        self.port = serialport
        self.logger = logger

    def run(self):
        self.port.write("ru".encode())

    def stop(self):
        self.port.write("st".encode())

    def pressure(self) -> int:
        try:
            self.port.write("pr".encode())
            response = self.port.readline().decode()
            psi = response.split(",")[1][:-1]
            return int(psi)
        except Exception as e:
            if self.logger is not None:
                self.logger.critical(f"Reading failed on {self.port.port}")
                self.logger.exception(e)
            return -1

    def close(self):
        self.port.close()

    def open(self):
        self.port.open()
