from .ob.orderbook_wrapper import OrderBookWrapper


class Simulator(object):
    """
    Base simulator for running orderbook
    over simulated and historical data
    """

    def __init__(self, options, snapshot=None, raw_data=None):
        super(Simulator, self).__init__()
        if snapshot:
            self.data_dir = options["snapshot_dir"]
            self.orderbook = OrderBookWrapper(symbol=options["symbol"],
                                              delta=0,
                                              data_type="snapshot",
                                              input_data=snapshot)
        elif raw_data:
            self.data_dir = options["raw_data_dir"]
            self.orderbook = OrderBookWrapper(symbol=options["symbol"],
                                              delta=0,
                                              data_type="snapshot",
                                              input_data=raw_data)

        self.time = 0

    def rewind(self, time_length):
        pass

    def forward(self, time_length):
        pass

    def place(self, side, price, volume):
        """Places an order to the simulated orderbook

        Arguments:
            side {string} -- side of orderbook
            price {float} -- price of order
            volume {float} -- volume of order
        """
        pass
