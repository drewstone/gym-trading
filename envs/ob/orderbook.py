import numpy as np
from datetime import datetime as dt
from .order_utils import Order, PriceLevel
from .orderbook_interface import OrderBookInterface


class OrderBook(OrderBookInterface):
    """
    An orderbook class that inherits an OrderBookInterface.
    The book maintains two dictionaries for two sides of
    the book. Each side is a (float, PriceLevel) dict.

    Extends:
        OrderBookInterface
    """

    def __init__(self, symbol, delta=0):
        """
        Initializes a new OrderBook

        The OrderBook has functionality for reconstruction
        of live and snapshotted data across a specific symbol

        Arguments:
            symbol {String} -- symbol of particular orderbook

        Keyword Arguments:
            delta {number} -- for relative/absolute orderbook modes
                                (NOT IMPLEMENTED)
        """
        super(OrderBook, self).__init__()
        self.symbol = symbol
        self.delta = delta

    def refresh(self):
        """
        Refreshes state of orderbook included all features
        """
        self.bid = max(self._bid_limits.keys()) if len(
            self._bid_limits.keys()) > 0 else 0
        self.ask = min(self._ask_limits.keys()) if len(
            self._ask_limits.keys()) > 0 else float(9999999999)

        self.bid_vol = self._bid_limits[self.bid].total_vol if len(
            self._bid_limits.keys()) > 0 else 0
        self.ask_vol = self._ask_limits[self.ask].total_vol if len(
            self._ask_limits.keys()) > 0 else 0

        self.spread = self.ask - self.bid
        self.midquote = (self.ask + self.bid) / 2.0

        self.imbalance = -np.log(self.bid_vol / self.ask_vol) if len(
            self._bid_limits.keys()) > 0 and len(
            self._ask_limits.keys()) > 0 else 0

        total_bid_vol = sum(list(map(
            lambda lvl: lvl.total_vol, self._bid_limits.values())))
        total_ask_vol = sum(list(map(
            lambda lvl: lvl.total_vol, self._ask_limits.values())))
        self.misbalance = -(total_ask_vol - total_bid_vol)

        smart_bid = self.bid * (1.0 / self.bid_vol) if len(
            self._bid_limits.keys()) > 0 else 0
        smart_ask = self.ask * (1.0 / self.ask_vol) if len(
            self._ask_limits.keys()) > 0 else 0
        self.smart_price = (smart_bid + smart_ask) / 2.0

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
                volume, filled, remaining_vol = level.get(volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if volume > 0 or remaining_vol == 0:
                    del self._ask_limits[key]
                else:
                    break

        elif side == "ASK":
            for key in self._bid_limits.keys():
                level = self._bid_limits[key]
                volume, filled, remaining_vol = level.get(volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if volume > 0 or remaining_vol == 0:
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
                order.volume, filled, remaining_vol = level.get(order.volume)
                print(order.volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if order.volume > 0 or remaining_vol == 0:
                    del self._ask_limits[key]
                else:
                    break

            if order.volume > 0:
                if price not in self._bid_limits:
                    self._bid_limits[price] = PriceLevel(price)
                self._bid_limits[price].put(order)

        elif side == "ASK":
            for key in [i for i in self._bid_limits.keys() if i >= price]:
                level = self._bid_limits[key]
                order.volume, filled, remaining_vol = level.get(order.volume)
                filled_orders = filled_orders + filled

                # if leftover volume, we've cleared the price level's volume
                if order.volume > 0 or remaining_vol == 0:
                    del self._bid_limits[key]
                else:
                    break

            if order.volume > 0:
                if price not in self._ask_limits:
                    self._ask_limits[price] = PriceLevel(price)
                self._ask_limits[price].put(order)

        for o in filled_orders:
            print("ooo : MARKETABLE | sym = {}, side = {}, add_ts = {}, "
                  "trade_ts = {}, price = {}, vol = {}".format(self.symbol,
                                                               side,
                                                               o.timestamp,
                                                               dt.now(),
                                                               o.price,
                                                               o.volume))
        if order.volume > 0:
            print("ooo : LIMIT | sym = {}, side = {}, ts = {}, "
                  "price = {}, vol = {}".format(self.symbol,
                                                side,
                                                order.timestamp,
                                                order.price,
                                                order.volume))

        # refresh orderbook state
        self.refresh()
