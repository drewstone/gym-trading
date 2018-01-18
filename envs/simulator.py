from datetime import datetime
from ob.orderbook import OrderBook
from ob.processor import DataProcessor


class Simulator(object):
    """
    Base simulator for running orderbook
    over simulated and historical data
    """

    def __init__(self, options):
        """Initializes a simulator with various input data sources

        The simulator will maintain a limit order book for a
        particular symbol and maintain PNL, etc of simulated orders

        Arguments:
            options {object} -- configuration options for simulator
                                including data dirs, formats, etc.
        """
        super(Simulator, self).__init__()
        self.grid_step_length = options["grid_step_length"]
        self.data_format = options["data_format"]
        self.agents = []
        self.finished = False

        self.data_proc = DataProcessor(
            data_dir=options["data_dir"],
            data_format=options["data_format"],
            dates=options["dates"],
            exchange=options["exchange"])

        self.orderbook = OrderBook(
            symbol=options["symbol"],
            delta=options["delta"])

    def step(self, time_length=1):
        if self.data_format == "raw":
            data = self.data_proc.next(time_length)

            for inx, order in enumerate(data):
                ts = datetime.strptime("{},{},{}".format(
                    order.date, order.time, order.millis),
                    "%Y-%m-%d,%H:%M:%S,%f")

                if order.side == "buy":
                    if order.order_type == "limit":
                        self.orderbook.limit(
                            "BID", order.price, order.volume, ts)
                    elif order.order_type == "market":
                        self.orderbook.market(
                            "BID", order.price, order.volume, ts)
                elif order.side == "sell":
                    if order.order_type == "limit":
                        self.orderbook.limit(
                            "ASK", order.price, order.volume, ts)
                    elif order.order_type == "market":
                        self.orderbook.market(
                            "ASK", order.price, order.volume, ts)
                else:
                    raise ValueError("Invalid order side")
        elif self.data_format == "snapshot":
            data = self.data_proc.next(time_length)

            # clear orderbook for new snapshot
            # TODO: leverage thrown away information
            self.orderbook.clear()

            ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp = data
            ts = datetime.strptime("{}".format(
                timestamp), "%Y-%m-%d %H:%M:%S")

            for inx, bid in enumerate(bid_prices):
                self.orderbook.limit("BID", bid, bid_volumes[inx], ts)

            for inx, ask in enumerate(ask_prices):
                self.orderbook.limit("ASK", ask, ask_volumes[inx], ts)
        else:
            raise ValueError("Invalid data format")
