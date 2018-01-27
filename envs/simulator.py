import pprint
import copy
from datetime import datetime
from ob.orderbook import OrderBook
from ob.processor import DataProcessor, OrderEntry
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

        self.symbol = options["symbol"]
        self.delta = options["delta"]
        self.data_format = options["data_format"]
        self.exchange = options["exchange"]
        self.date_range = options["dates"]

        self.first_date = self.date_range[0]
        self.curr_date = self.date_range[0]
        self.final_date = self.date_range[1]
        self.last_time = 0
        self.finished = False

        # initialize data processors and books for each day
        self.data_path = lambda date: "{}/{}_order_book_{}.csv".format(
            options["data_dir"], options["symbol"], date)
        self.set_data_processors()

    def is_finished(self):
        return self.finished

    def set_data_processors(self):

        # if we are on first date, initialize processor and orderbook
        if self.first_date == self.curr_date:
            self.current_processor = DataProcessor(
                file_str=self.data_path(self.curr_date),
                exchange=self.exchange,
                data_format=self.data_format)

            self.next_processor = self.fast_forward_processor()
            self.orderbook = self.setup_orderbook()
        elif self.final_date == self.curr_date:
            self.current_processor = self.next_processor
            self.next_processor = None
        else:
            self.current_processor = self.next_processor
            self.next_processor = self.fast_forward_processor()

        self.curr_date += 1

    def fast_forward_processor(self):
        processor = DataProcessor(
            data_format=self.data_format,
            file_str=self.data_path(self.curr_date + 1),
            exchange=self.exchange)

        order = processor.next()[0]
        while order.event_type == "Initial":
            # pull next order
            order = processor.next()[0]

        processor.leftover_order = order
        return processor

    def setup_orderbook(self):
        self.orderbook = OrderBook(
            symbol=self.symbol,
            delta=self.delta)

        order = self.current_processor.next()[0]

        self.process_order(order)
        while order.event_type == "Initial":
            # pull next order
            order = self.current_processor.next()[0]
            self.process_order(order)

        return self.orderbook

    def next(self, time_length=None):
        try:
            data = self.current_processor.next(time_length)
        except StopIteration:
            if self.next_processor is None:
                self.finished = True
                return

            self.set_data_processors()
            return self.next(time_length)

        if self.data_format == "raw":
            for inx, order in enumerate(data):
                self.process_order(order)

        elif self.data_format == "snapshot":
            self.orderbook.clear()

            ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp = data
            ts = self.curr_datetime.strptime("{}".format(
                timestamp), "%Y-%m-%d %H:%M:%S")

            for inx, bid in enumerate(bid_prices):
                self.orderbook.limit(
                    "BID", bid, bid_volumes[inx], ts)

            for inx, ask in enumerate(ask_prices):
                self.orderbook.limit(
                    "ASK", ask, ask_volumes[inx], ts)
        else:
            raise ValueError("Invalid data format")

        return self.orderbook

    def value(self, side, volume):
        cloned_book = copy.deepcopy(self.orderbook)
        filled_orders = cloned_book.market(side, volume, self.curr_time)
        return sum(list(map(
            lambda order: order.filled_volume * order.price, filled_orders)))

    def process_order(self, order):
        if order.date and order.time and order.millis:
            ts = datetime.strptime("{},{},{}".format(
                order.date, order.time, order.millis),
                "%Y-%m-%d,%H:%M:%S,%f")
        else:
            ts = self.time

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
                self.orderbook.immediate_or_cancel(
                    side=side,
                    price=order.price,
                    volume=order.volume,
                    timestamp=ts,
                    order_id=order.order_id)
            elif order.exec_opt == "maker-or-cancel":
                self.orderbook.maker_or_cancel(
                    side=side,
                    price=order.price,
                    volume=order.volume,
                    timestamp=ts,
                    order_id=order.order_id)
            else:
                if order.order_type == "limit":
                    self.orderbook.limit(
                        side=side,
                        price=order.price,
                        volume=order.volume,
                        timestamp=ts,
                        order_id=order.order_id)
                elif order.order_type == "market":
                    self.orderbook.market(
                        side=side,
                        volume=order.volume,
                        timestamp=ts,
                        order_id=order.order_id)
        elif order.event_type == "Cancel":
            self.orderbook.cancel(
                side=side,
                order_id=order.order_id)

        elif order.event_type == "FILL":
            pass

    def place(self, order_type, side, price, volume):
        order = OrderEntry({
            "evt_type": "Place",
            "price": price,
            "side": side,
            "volume": volume,
            "type": order_type})
        self.process_order(order)
