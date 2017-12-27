class Order(object):
    """
    An order class that prioritizes
    timestamp for comparison behavior
    """
    def __init__(self, timestamp, price, volume):
        super(Order, self).__init__()
        self._timestamp = timestamp
        self._price = price
        self._volume = volume

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid timestamp")

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid price")

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")

    def __cmp__(self, other):
        return self.timestamp < other.timestamp
