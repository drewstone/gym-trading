class SimulatorInterface(object):
    def __init__(self):
        super(SimulatorInterface, self).__init__()
        self._time = 0
        self._pnl = 0
        self._cash = 0
        self._positions = 0

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._time = float(val)

    @property
    def pnl(self):
        return self._pnl

    @pnl.setter
    def pnl(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._pnl = float(val)

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._cash = float(val)

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._positions = float(val)
