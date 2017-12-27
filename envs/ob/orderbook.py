from datatime import datetime as dt
from .order_utils import Order, PriceLevel
from .orderbook_wrapper import OrderBookWrapper


class OrderBook(OrderBookWrapper):
    def __init__(self, symbol, snapshot=None):
        super(OrderBook, self).__init__()
        self.symbol = symbol

        if snapshot:
            self.set_snapshot(snapshot)
            self.refresh()

    def set_snapshot(self, snapshot):
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

    def add_order(self, side, price, volume):
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
