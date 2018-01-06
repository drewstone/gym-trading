from datetime import datetime as dt
from bintrees import FastRBTree
from .order_utils import PriceLevel, Order


class Tree(object):

    def __init__(self):
        self.price_tree = FastRBTree()
        self.volume = 0
        self.price_map = {}  # Map from price -> PriceLevel object
        self.order_map = {}  # Order ID to Order object
        self.min_price = None
        self.max_price = None

    def __len__(self):
        return len(self.order_map)

    def get_price(self, price):
        return self.price_map[price]

    def get_order(self, id_num):
        return self.order_map[id_num]

    def fill(self, price, volume, pt):
        """Fill a certain volume in the order tree

        This function allows interoperability between market
        and marketable limit order fills. When the price is
        non-zero, it represents purchasing a specified volume
        up to a certain price. Otherwise, a zero-valued price
        represents a market order for a specified volume

        Arguments:
            price {float} -- price of marketable limit order
            volume {float} -- volume to attempt to fill
            pt {str} -- purchase type (BUY or SELL)

        Returns:
            tuple<float, array> -- remaining volume and all filled orders
        """
        filled_orders = []

        while volume > 0:
            curr = self.min() if pt == "BUY" else self.max()

            # safety check when orderbook has been cleared
            if curr is None:
                break

            # non-zero price constitutes marketable limit execution
            if price > 0:
                # indicator when bid/ask is lower/higher than price
                cond = price >= curr if pt == "BUY" else price <= curr
            else:
                cond = True

            if cond:
                pl = self.get_price(curr)
                volume, fills, leftover_vol = pl.get(volume)
                filled_orders += fills

                # check if we've executed entire price level
                if leftover_vol == 0:
                    self.remove_price(curr)
            else:
                # break when current bid/ask is higher/lower than price
                break

        # remove completely filled orders
        for order in filled_orders:
            # update tree volume
            self.volume -= order.filled_volume
            if order.volume == 0:
                del self.order_map[order.id]

        return volume, filled_orders

    def create_price(self, price):
        """Create a new pricelevel in the order tree

        Every order lives in a PriceLevel object, a heap
        based list containing all orders at that price. This
        function creates those lists when they don't exist.

        Arguments:
            price {float} -- price of new price level
        """
        new_list = PriceLevel(price)
        self.price_tree.insert(price, new_list)
        self.price_map[price] = new_list
        if self.max_price is None or price > self.max_price:
            self.max_price = price
        if self.min_price is None or price < self.min_price:
            self.min_price = price

    def remove_price(self, price):
        self.price_tree.remove(price)
        del self.price_map[price]

        if self.max_price == price:
            try:
                self.max_price = max(self.price_tree)
            except ValueError:
                self.max_price = None
        if self.min_price == price:
            try:
                self.min_price = min(self.price_tree)
            except ValueError:
                self.min_price = None

    def price_exists(self, price):
        return price in self.price_map

    def order_exists(self, id_num):
        return id_num in self.order_map

    def insert_order(self, id_num, price, vol, timestamp=dt.now()):
        if price not in self.price_map:
            self.create_price(price)
        order = Order(id_num, price, vol, timestamp, self.price_map[price])
        self.order_map[order.id] = order
        self.volume += order.volume

    def update_order(self, id_num, price, volume):
        order = self.order_map[id_num]
        original_volume = order.volume
        if price != order.price:
            # Price changed
            price_level = self.price_map[order.price]
            price_level.remove(order)
            if len(price_level) == 0:
                self.remove_price(order.price)
            self.insert_order(id_num, price, volume)
            self.volume -= original_volume
        else:
            # Quantity changed
            order.update_volume(volume)
            self.volume += order.volume - original_volume

    def remove_order_by_id(self, id_num):
        order = self.order_map[id_num]
        self.volume -= order.volume
        order.price_level.remove(order)
        if len(order.price_level) == 0:
            self.remove_price(order.price)
        del self.order_map[id_num]

    def max(self):
        return self.max_price

    def min(self):
        return self.min_price
