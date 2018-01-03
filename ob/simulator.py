from .orderbook_wrapper import OrderBookWrapper


class Simulator(object):
    """
    Base simulator for running orderbook
    over simulated and historical data
    """

    def __init__(self, options, snapshot=None, raw_data=False):
        """Initializes a simulator with various input data sources

        The simulator will maintain a limit order book for a
        particular symbol and maintain PNL, etc of simulated orders

        Arguments:
            options {object} -- configuration options for simulator
                                including data directories


        Keyword Arguments:
            snapshot {object} -- A snapshot of a limit order book
                                (bid/ask orders) (default: {None})
            raw_data {array} -- An array of orders to initialize book
                                 (default: {False})
        """
        super(Simulator, self).__init__()
        self.time = 0
        self.time_length = options['time_length']
        if raw_data:
            self.orderbook = OrderBookWrapper(symbol=options["symbol"],
                                              delta=0,
                                              data_type="raw_data",
                                              input_data=snapshot)
        elif raw_data:
            self.orderbook = OrderBookWrapper(symbol=options["symbol"],
                                              delta=0,
                                              data_type="raw_data",
                                              input_data=raw_data)

        self.time = 0

    def rewind(self, time_length):
        pass

    def forward(self, time_length):
        pass

    def place(self, side, price, volume):
        """Places an order to the simulated orderbook

        Arguments:
            side {str} -- side of orderbook
            price {float} -- price of order
            volume {float} -- volume of order
        """
        pass
