from .ordertree import Tree


class OrderBookInterface(object):
    """
    A blank orderbook that tracks
    information/state about the book
    """

    # constant error ask
    # TODO: Change to enum or something other than number
    error_ask = float(9999999999)

    def __init__(self):
        """Initialize an orderbook with bid/ask order trees

        The orderbook interface represents a blank orderbook state
        """
        super(OrderBookInterface, self).__init__()
        self._bid = 0
        self._ask = self.error_ask
        self._ask_vol = 0
        self._bid_vol = 0
        self._spread = 0
        self._midquote = 0
        self._bid_limits = Tree()
        self._ask_limits = Tree()

    def clear(self):
        self._bid = 0
        self._ask = self.error_ask
        self._ask_vol = 0
        self._bid_vol = 0
        self._spread = 0
        self._midquote = 0
        self._bid_limits = Tree()
        self._ask_limits = Tree()

    @property
    def bid(self):
        return self._bid

    @bid.setter
    def bid(self, val):
        if val > self.error_ask or val < 0 or val is None:
            raise ValueError("Invalid bid {}".format(val))
        self._bid = float(val)

    @property
    def ask(self):
        return self._ask

    @ask.setter
    def ask(self, val):
        if val > self.error_ask or val < 0 or val is None:
            raise ValueError("Invalid ask {}".format(val))
        self._ask = float(val)

    @property
    def bid_vol(self):
        return self._bid_vol

    @bid_vol.setter
    def bid_vol(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume {}".format(val))
        self._bid_vol = float(val)

    @property
    def ask_vol(self):
        return self._ask_vol

    @ask_vol.setter
    def ask_vol(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume {}".format(val))
        self._ask_vol = float(val)

    @property
    def spread(self):
        return self._spread

    @spread.setter
    def spread(self, val):
        self._spread = val

    @property
    def midquote(self):
        return self._midquote

    @midquote.setter
    def midquote(self, val):
        self._midquote = val

    def to_vec(self, threshold=10):
        bid_prices, bid_vols = [], []
        ask_prices, ask_vols = [], []

        for inx, elt in enumerate(self._bid_limits.price_tree.items(reverse=True)):
            bid_prices.append(elt[0])
            bid_vols.append(elt[1].total_vol)

        for inx, elt in enumerate(self._ask_limits.price_tree.items()):
            ask_prices.append(elt[0])
            ask_vols.append(elt[1].total_vol)

        vector = []
        for i in range(threshold):
            vector.append(ask_prices[i])
            vector.append(ask_vols[i])
            vector.append(bid_prices[i])
            vector.append(bid_vols[i])

        return vector

    def __str__(self):
        value = "\nAsks\t\t\t\t\t\t\tBids"

        # TODO: Make something useful out of this
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
