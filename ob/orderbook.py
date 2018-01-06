from datetime import datetime as dt
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
        """Initializes a new OrderBook

        The OrderBook has functionality for reconstruction
        of live and snapshotted data across a specific symbol

        Arguments:
            symbol {str} -- symbol of particular orderbook

        Keyword Arguments:
            delta {number} -- for relative/absolute orderbook modes
                                (NOT IMPLEMENTED)
        """
        super(OrderBook, self).__init__()
        self.order_count = 0
        self.symbol = symbol
        self.delta = delta

    def market(self, side, volume, timestamp=dt.now()):
        """Submit market orders to orderbook mechanism

        The market order function places a market order on
        the corresponding side of the orderbook for a given
        volume. Remaining volume does not get posted to the book;
        instead, use "limit" function for marketable limit orders.

        Arguments:
            side {str} -- side of orderbook to place order
            volume {float} -- volume of order

        Keyword Arguments:
            timestamp {datetime} -- time of order (default: {dt.now()})

        Raises:
            ValueError -- Invalid volume errors (no zero volume orders)
            ValueError -- Invalid side errors (only BID/ASK)
        """
        if volume == 0:
            raise ValueError("Invalid volume")

        if side == "BID":
            purchase_type = "BUY"
            search_tree = self._ask_limits
        elif side == "ASK":
            purchase_type = "SELL"
            search_tree = self._bid_limits
        else:
            raise ValueError("Invalid orderbook side")

        volume, filled_orders = search_tree.fill(0, volume, purchase_type)

        # log all filled orders
        for o in filled_orders:
            print("ooo : MARKET | sym = {}, order_id = {} side = {}, "
                  "add_ts = {}, trade_ts = {}, price = {}, filled = {}".format(
                      self.symbol,
                      self.order_count,
                      o.timestamp,
                      timestamp,
                      o.price,
                      o.filled_volume))

        # refresh orderbook state
        self.refresh()
        self.order_count += 1

    def limit(self, side, price, volume, timestamp=dt.now()):
        """Limit order/Marketable limit order function

        Allows for adding limit orders into the orderbook.
        The limit order is checked for whether it is marketable
        in order to account for limit orders that are placed
        while prices are changing. Remaining order is posted
        to the corresponding side of the book.

        Arguments:
            side {str} -- side of the book
            price {float} -- price of limit order
            volume {float} -- volume of limit order

        Keyword Arguments:
            timestamp {datetime} -- time of order (default: {dt.now()})

        Raises:
            ValueError -- Invalid volume error
            ValueError -- Invalid price error
        """
        if volume == 0:
            raise ValueError("Invalid volume")
        if price <= 0:
            raise ValueError("Invalid price")

        if side == "BID":
            purchase_type = "BUY"
            search_tree = self._ask_limits
            order_tree = self._bid_limits
        elif side == "ASK":
            purchase_type = "SELL"
            search_tree = self._bid_limits
            order_tree = self._ask_limits
        else:
            raise ValueError("Invalid orderbook side")

        # attempt to execute marketable limit orders
        volume, filled_orders = search_tree.fill(price, volume, purchase_type)

        # log all filled orders
        for o in filled_orders:
            print("ooo : TRADE | sym = {}, side = {}, add_ts = {}, "
                  "trade_ts = {}, price = {}, filled_vol = {}".format(
                      self.symbol,
                      side,
                      o.timestamp,
                      dt.now(),
                      o.price,
                      o.filled_volume))

        # log newly placed limit order
        if volume > 0:
            order_tree.insert_order(self.order_count, price, volume, timestamp)
            print("ooo : LIMIT | sym = {}, order_id = {}, side = {}, "
                  "ts = {}, price = {}, vol = {}".format(self.symbol,
                                                         self.order_count,
                                                         side,
                                                         timestamp,
                                                         price,
                                                         volume))

        # refresh orderbook state
        self.refresh()
        self.order_count += 1

    def refresh(self):
        """Refreshes state of orderbook included all features

        After each state change to the orderbook, we want to
        recompute simple stateful properties about the book

        Raises:
            ValueError -- Invalid ask errors
        """
        try:
            self.bid = self._bid_limits.max()
        except Exception:
            self.bid = 0

        try:
            self.ask = self._ask_limits.min()
        except Exception:
            self.ask = self.error_ask

        try:
            self.bid_vol = self._bid_limits.get_price(self.bid).total_vol
        except Exception:
            self.bid_vol = 0

        try:
            self.ask_vol = self._ask_limits.get_price(self.ask).total_vol
        except Exception:
            self.ask_vol = 0

        try:
            if self.ask == self.error_ask:
                raise ValueError

            self.spread = self.ask - self.bid
        except Exception:
            self.spread = None

        try:
            if self.ask == self.error_ask:
                raise ValueError

            self.midquote = (self.ask + self.bid) / 2.0
        except Exception:
            self.midquote = None
