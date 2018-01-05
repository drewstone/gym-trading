from .ordertree import Tree


class OrderBookInterface(object):
    """
    A blank orderbook that tracks
    information/state about the book
    """

    error_ask = float(9999999999)

    def __init__(self):
        super(OrderBookInterface, self).__init__()
        self._bid = 0
        self._ask = self.error_ask
        self._ask_vol = 0
        self._bid_vol = 0
        self._spread = 0
        self._imbalance = 0
        self._misbalance = 0
        self._smart_price = 0
        self._midquote = 0
        self._bid_limits = Tree()
        self._ask_limits = Tree()

    def clear(self):
        self._bid = 0
        self._ask = self.error_ask
        self._ask_vol = 0
        self._bid_vol = 0
        self._spread = 0
        self._imbalance = 0
        self._misbalance = 0
        self._smart_price = 0
        self._midquote = 0
        self._bid_limits = Tree()
        self._ask_limits = Tree()

    @property
    def bid(self):
        return self._bid

    @bid.setter
    def bid(self, val):
        if val > self.error_ask or val < 0 or val is None:
            raise ValueError("Invalid bid")
        self._bid = float(val)

    @property
    def ask(self):
        return self._ask

    @ask.setter
    def ask(self, val):
        if val > self.error_ask or val < 0 or val is None:
            raise ValueError("Invalid ask")
        self._ask = float(val)

    @property
    def bid_vol(self):
        return self._bid_vol

    @bid_vol.setter
    def bid_vol(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._bid_vol = float(val)

    @property
    def ask_vol(self):
        return self._ask_vol

    @ask_vol.setter
    def ask_vol(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._ask_vol = float(val)

    @property
    def imbalance(self):
        return self._imbalance

    @imbalance.setter
    def imbalance(self, val):
        if val is None:
            raise ValueError("Invalid imbalance")
        self._imbalance = float(val)

    @property
    def spread(self):
        return self._spread

    @spread.setter
    def spread(self, val):
        if val < 0:
            raise ValueError("Invalid volume")
        self._spread = float(val)

    @property
    def misbalance(self):
        return self._misbalance

    @misbalance.setter
    def misbalance(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._misbalance = float(val)

    @property
    def smart_price(self):
        return self._smart_price

    @smart_price.setter
    def smart_price(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._smart_price = float(val)

    @property
    def midquote(self):
        return self._midquote

    @midquote.setter
    def midquote(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._midquote = float(val)

    def __str__(self):
        value = "\nAsks\t\t\t\t\t\t\tBids"
        for i in range(max(len(self._ask_limits.values()),
                           len(self._bid_limits.values()))):
            value += "\nprice: {} | volume: {}{}price: {} | volume: {}".format(
                "", "", "", "", "")

        return "\nprice: {} | volume: {}{}price: {} | volume: {}".format(
            value,
            self.ask,
            self.ask_vol,
            "\t\t\t\t",
            self.bid,
            self.bid_vol)
