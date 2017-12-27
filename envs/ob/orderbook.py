from datatime import datetime as dt
from .order_utils import Order, PriceLevel
from .orderbook_wrapper import OrderBookWrapper


class OrderBook(OrderBookWrapper):
    """
    An orderbook class that inherits an OrderBookWrapper.
    The book maintains two dictionaries for two sides of
    the book. Each side is a (float, PriceLevel) dict.

    Extends:
        OrderBookWrapper
    """
    def __init__(self, symbol, snapshot=None):
        """
        Initializes a new OrderBook

        The OrderBook has functionality for reconstruction
        of live and snapshotted data across a specific symbol

        Arguments:
            symbol {String} -- symbol of particular orderbook

        Keyword Arguments:
            snapshot {Tupe} -- Tuple containing bid/ask price/vol data
                               (default: {None})
        """
        super(OrderBook, self).__init__()
        self.symbol = symbol
        self.delta = 0

        if snapshot:
            self.set_snapshot(snapshot)
            self.refresh()

    def set_snapshot(self, snapshot):
        """
        Reconstructs orderbook state from a given snapshot

        To be used across longer time-span orderbook datasets
        such as 3 second or minutely orderbook snapshots

        Arguments:
            snapshot {Tuple} -- Tuple containing bid/ask price/vol data
        """
        bids, bid_vols, asks, ask_vols = snapshot

        for inx, bid in enumerate(bids):
            if not bid in self._bid_limits:
                self._bid_limits[bid] = PriceLevel(bid)
            order = Order(inx, bid, bid_vols[inx])
            self._bid_limits[bid].put(order)

        for inx, ask in enumerate(asks):
            if not ask in self._ask_limits:
                self._ask_limits[ask] = PriceLevel(ask)
            order = Order(inx, ask, ask_vols[inx])
            self._ask_limits[ask].put(order)

    def market(self, side, volume):
        """
        Market order function

        The market order function places a market order on
        the corresponding side of the orderbook for a given
        volume. Remaining volume does not get posted to the book;
        instead, use "limit" function for marketable limit orders.

        Arguments:
            side {String} -- side of orderbook to place order
            volume {float} -- volume of order

        Raises:
            ValueError -- Invalid volume error
        """
        if volume == 0:
            raise ValueError("Invalid volume")

        timestamp = dt.now()
        filled_orders = []
        if side == "BID":
            for key in self._ask_limits.keys():
                level = self._ask_limits[key]
                volume, filled = level.get(volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if volume > 0:
                    del self._ask_limits[key]
                else:
                    break

        elif side == "ASK":
            for key in self._bid_limits.keys():
                level = self._bid_limits[key]
                volume, filled = level.get(volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if volume > 0:
                    del self._bid_limits[key]
                else:
                    break

        for o in filled_orders:
            print("ooo : MARKET | sym = {}, side = {}, add_ts = {}"
                  ", trade_ts = {}, price = {}, vol = {}".format(self.symbol,
                                                                 o.timestamp,
                                                                 timestamp,
                                                                 o.price,
                                                                 o.volume))

    def limit(self, side, price, volume):
        """
        Limit order/Marketable limit order function

        Allows for adding limit orders into the orderbook.
        The limit order is checked for whether it is marketable
        in order to account for limit orders that are placed
        while prices are changing. Remaining order is posted
        to the corresponding side of the book.

        Arguments:
            side {String} -- side of the book
            price {float} -- price of limit order
            volume {float} -- volume of limit order

        Raises:
            ValueError -- Invalid volume error
            ValueError -- Invalid price error
        """
        if volume == 0:
            raise ValueError("Invalid volume")
        if price <= 0:
            raise ValueError("Invalid price")

        timestamp = dt.now()
        order = Order(timestamp, price, volume)

        filled_orders = []
        if side == "BID":
            for key in [i for i in self._ask_limits.keys() if i <= price]:
                level = self._ask_limits[key]
                order.volume, filled = level.get(order.volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if order.volume > 0:
                    del self._ask_limits[key]
                else:
                    break

            if order.volume > 0:
                self._bid_limits[price].put(order)

        elif side == "ASK":
            for key in [i for i in self._bid_limits.keys() if i >= price]:
                level = self._bid_limits[key]
                order.volume, filled = level.get(order.volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if order.volume > 0:
                    del self._bid_limits[key]
                else:
                    break

            if order.volume > 0:
                self._ask_limits[price].put(order)

        for o in filled_orders:
            print("ooo : MARKETABLE | sym = {}, side = {}, add_ts = {}"
                  ", trade_ts = {}, price = {}, vol = {}".format(self.symbol,
                                                                 o.timestamp,
                                                                 dt.now(),
                                                                 o.price,
                                                                 o.volume))

        print("ooo : LIMIT | sym = {}, side = {}, ts = {},"
              "price = {}, vol = {}".format(self.symbol,
                                            side,
                                            order.timestamp,
                                            order.price,
                                            order.volume))
