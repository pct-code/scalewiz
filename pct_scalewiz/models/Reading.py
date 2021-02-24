"""Model for a Reading object."""


class Reading:
    def __init__(self, index, elapsed, psi1, psi2):
        self.index = index
        self.elapsed = elapsed
        self.psi1 = psi1
        self.psi2 = psi2
