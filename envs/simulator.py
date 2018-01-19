from multiprocessing.dummy import Pool as ThreadPool 
import pprint
from datetime import datetime
from ob.orderbook import OrderBook
from ob.processor import DataProcessor
pp = pprint.PrettyPrinter(indent=4)


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

        self.dates = options["dates"]
        self.data_procs = {}
        self.orderbooks = {}

        for date in self.dates:
            self.data_procs[date] = DataProcessor(
                data_dir=options["data_dir"],
                data_format=options["data_format"],
                date=date,
                exchange=options["exchange"])

            self.orderbooks[date] = OrderBook(
                symbol=options["symbol"],
                delta=options["delta"])

    def initialize_raw(self):
        pool = ThreadPool(4)
        obs = pool.map(self.setup_orderbook, self.dates)
        pool.close()
        pool.join()

        result = {}
        for inx, date in enumerate(self.dates):
            result[date] = obs[inx]

        return result

    def setup_orderbook(self, date):
        data = self.data_procs[date].next()
        order = data[0]

        while order.event_type == "Initial":
            ts = datetime.strptime("{},{},{}".format(
                order.date, order.time, order.millis),
                "%Y-%m-%d,%H:%M:%S,%f")

            side = "BID" if order.side == "buy" else "ASK"
            if order.event_type == "Place" or order.event_type:
                if order.exec_opt == "immediate-or-cancel":
                    self.orderbooks[date].immediate_or_cancel(
                        side=side,
                        price=order.price,
                        volume=order.volume,
                        timestamp=ts,
                        order_id=order.order_id)
                elif order.exec_opt == "maker-or-cancel":
                    self.orderbooks[date].maker_or_cancel(
                        side=side,
                        price=order.price,
                        volume=order.volume,
                        timestamp=ts,
                        order_id=order.order_id)
                else:
                    if order.order_type == "limit":
                        self.orderbooks[date].limit(
                            side=side,
                            price=order.price,
                            volume=order.volume,
                            timestamp=ts,
                            order_id=order.order_id)
                    elif order.order_type == "market":
                        self.orderbooks[date].market(
                            side=side,
                            price=order.price,
                            volume=order.volume,
                            timestamp=ts,
                            order_id=order.order_id)
            elif order.event_type == "Cancel":
                self.orderbooks[date].cancel(
                    side=side,
                    order_id=order.order_id)

            elif order.event_type == "FILL":
                pass

            # pull next order
            data = self.data_procs[date].next()
            order = data[0]

        return self.orderbooks[date]

    def step(self, date, time_length=1):
        if self.data_format == "raw":
            data = self.data_procs[date].next(time_length)

            for inx, order in enumerate(data):
                if not order:
                    continue

                ts = datetime.strptime("{},{},{}".format(
                    order.date, order.time, order.millis),
                    "%Y-%m-%d,%H:%M:%S,%f")

                side = "BID" if order.side == "buy" else "ASK"
                if order.event_type == "Place" or order.event_type:
                    if order.exec_opt == "immediate-or-cancel":
                        self.orderbooks[date].immediate_or_cancel(
                            side=side,
                            price=order.price,
                            volume=order.volume,
                            timestamp=ts,
                            order_id=order.order_id)
                    elif order.exec_opt == "maker-or-cancel":
                        self.orderbooks[date].maker_or_cancel(
                            side=side,
                            price=order.price,
                            volume=order.volume,
                            timestamp=ts,
                            order_id=order.order_id)
                    else:
                        if order.order_type == "limit":
                            self.orderbooks[date].limit(
                                side=side,
                                price=order.price,
                                volume=order.volume,
                                timestamp=ts,
                                order_id=order.order_id)
                        elif order.order_type == "market":
                            self.orderbooks[date].market(
                                side=side,
                                volume=order.volume,
                                timestamp=ts,
                                order_id=order.order_id)
                elif order.event_type == "Cancel":
                    self.orderbooks[date].cancel(
                        side=side,
                        order_id=order.order_id)

                elif order.event_type == "FILL":
                    pass
        elif self.data_format == "snapshot":
            data = self.data_procs[date].next(time_length)

            # clear orderbook for new snapshot
            # TODO: leverage thrown away information
            self.orderbooks[date].clear()

            ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp = data
            ts = datetime.strptime("{}".format(
                timestamp), "%Y-%m-%d %H:%M:%S")

            for inx, bid in enumerate(bid_prices):
                self.orderbooks[date].limit("BID", bid, bid_volumes[inx], ts)

            for inx, ask in enumerate(ask_prices):
                self.orderbooks[date].limit("ASK", ask, ask_volumes[inx], ts)
        else:
            raise ValueError("Invalid data format")

        return self.orderbooks[date]
