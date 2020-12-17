"""Serial port wrapper for MX-class Teledyne pumps."""

class TeledynePump:
    def __init__(self, serialport):
        self.port = serialport

    def run(self):
        self.port.write("ru".encode())

    def stop(self):
        self.port.write("st".encode())

    def pressure(self) -> int:
        try:
            self.port.write("pr".encode())
            response = self.port.readline().decode()
            print(response)
            psi = response.split(',')[1][:-1]
            print(psi)
            return int(psi)
        except Exception:
            print("Reading failed")
            return 0
    
    def close(self):
        self.port.close()

    def open(self):
        self.port.open()

