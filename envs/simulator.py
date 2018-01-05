from datetime import datetime
from ob.orderbook import OrderBook
from ob.processor import DataProcessor
from .simulator_interface import SimulatorInterface


class Simulator(SimulatorInterface):
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
        self.traders = []
        self.finished = False

        self.data_proc = DataProcessor(
            data_dir=options["data_dir"],
            data_format=options["data_format"],
            dates=options["dates"],
            exchange=options["exchange"])

        self.orderbook = OrderBook(
            symbol=options["symbol"],
            delta=options["delta"])

    def start(self):
        self.step()

    def step(self, count=1):
        data = self.data_proc.next(count)

        if self.data_format == "raw":
            ts = datetime.strptime("{},{},{}".format(
                data.date, data.time, data.millis),
                "%Y-%m-%d,%H:%M:%S,%f")

            if data.side == "buy":
                if data.order_type == "limit":
                    self.orderbook.limit("BID", data.price, data.volume, ts)
                elif data.order_type == "market":
                    self.orderbook.market("BID", data.price, data.volume, ts)
            elif data.side == "sell":
                if data.order_type == "limit":
                    self.orderbook.limit("ASK", data.price, data.volume, ts)
                elif data.order_type == "market":
                    self.orderbook.market("ASK", data.price, data.volume, ts)
            else:
                raise ValueError("Invalid order side")
        elif self.data_format == "snapshot":
            # clear orderbook for new snapshot
            # TODO: leverage thrown away information somehow?
            self.orderbook.clear()

            ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp = data

            for inx, bid in enumerate(bid_prices):
                self.orderbook.limit("BID", bid, bid_volumes[inx])

            for inx, ask in enumerate(ask_prices):
                self.orderbook.limit("ASK", ask, ask_volumes[inx])
        else:
            raise ValueError("Invalid data format")

    def place(self, side, price, volume):
        """Places an order to the simulated orderbook

        Arguments:
            side {str} -- side of orderbook
            price {float} -- price of order
            volume {float} -- volume of order
        """
        pass

    def add_trader(self, trader):
        self.traders.append(trader)

    def is_finished(self):
        return self.finished
