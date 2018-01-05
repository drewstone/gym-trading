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

    def create_price(self, price):
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

    def update_order(self, target_order):
        order = self.order_map[target_order.id]
        original_volume = order.qty
        if target_order.price != order.price:
            # Price changed
            price_level = self.price_map[order.price]
            price_level.remove(order)
            if len(price_level) == 0:
                self.remove_price(order.price)
            self.insert_order(target_order)
            self.volume -= original_volume
        else:
            # Quantity changed
            order.update_qty(target_order.qty, target_order.price)
            self.volume += order.qty - original_volume

    def remove_order_by_id(self, id_num):
        order = self.order_map[id_num]
        self.volume -= order.volume
        order.price_level.remove(order)
        print(order.price_level)
        if len(order.price_level) == 0:
            self.remove_price(order.price)
        del self.order_map[id_num]

    def max(self):
        return self.max_price

    def min(self):
        return self.min_price
