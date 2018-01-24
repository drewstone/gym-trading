from multiprocessing.dummy import Pool as ThreadPool
import pprint
import copy
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

        # initialize data processors and books for each day
        for date in self.dates:
            self.data_procs[date] = DataProcessor(
                data_dir=options["data_dir"],
                data_format=options["data_format"],
                date=date,
                exchange=options["exchange"])

            self.orderbooks[date] = OrderBook(
                symbol=options["symbol"],
                delta=options["delta"])

        # set current time values
        self.curr_date = self.dates[0]
        self.curr_time = self.data_procs[self.curr_date].time

    def initialize_raw(self):
        pool = ThreadPool(4)
        obs = pool.map(self.setup_orderbook, self.dates)
        pool.close()
        pool.join()

        result = {}
        for inx, date in enumerate(self.dates):
            result[date] = obs[inx]

        return result

    def process_order(self, order, date):
        ts = datetime.strptime("{},{},{}".format(
            order.date, order.time, order.millis),
            "%Y-%m-%d,%H:%M:%S,%f")

        # pp.pprint({
        #     "event_id": order.event_id,
        #     "date": order.date,
        #     "time": order.time,
        #     "millis": order.millis,
        #     "order_id": order.order_id,
        #     "exec_opt": order.exec_opt,
        #     "event_type": order.event_type,
        #     "symbol": order.symbol,
        #     "order_type": order.order_type,
        #     "side": order.side,
        #     "timestamp": ts,
        # })

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

    def setup_orderbook(self):
        data = self.data_procs[self.curr_date].next()
        order = data[0]

        self.process_order(order, self.curr_date)
        while order.event_type == "Initial":
            # pull next order
            data = self.data_procs[self.curr_date].next()
            order = data[0]
            self.process_order(order, self.curr_date)

        return self.orderbooks[self.curr_date]

    def next(self, time_length=1):
        if self.data_format == "raw":
            data = self.data_procs[self.curr_date].next(time_length)

            for inx, order in enumerate(data):
                if not order:
                    continue
                else:
                    self.process_order(order, self.curr_date)

        elif self.data_format == "snapshot":
            data = self.data_procs[self.curr_date].next(time_length)

            # clear orderbook for new snapshot
            # TODO: leverage thrown away information
            self.orderbooks[self.curr_date].clear()

            ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp = data
            ts = self.curr_datetime.strptime("{}".format(
                timestamp), "%Y-%m-%d %H:%M:%S")

            for inx, bid in enumerate(bid_prices):
                self.orderbooks[self.curr_date].limit(
                    "BID", bid, bid_volumes[inx], ts)

            for inx, ask in enumerate(ask_prices):
                self.orderbooks[self.curr_date].limit(
                    "ASK", ask, ask_volumes[inx], ts)
        else:
            raise ValueError("Invalid data format")

        return self.orderbooks[self.curr_date]

    def value(self, side, volume):
        cloned_book = copy.deepcopy(self.orderbooks[self.curr_date])
        filled_orders = cloned_book.market(side, volume, self.curr_time)
        return sum(list(map(
            lambda order: order.filled_volume * order.price, filled_orders)))
