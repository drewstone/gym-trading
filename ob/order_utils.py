from functools import total_ordering
import heapq


class PriorityQueue(object):

    def __init__(self, initial=None, key=lambda x: x):
        self.key = key
        if initial:
            self._data = [(key(item), item) for item in initial]
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, item):
        heapq.heappush(self._data, (self.key(item), item))

    def pop(self):
        return heapq.heappop(self._data)[1]

    def remove(self, item):
        for i in range(len(self._data)):
            if self.key(self._data[i][1]) == self.key(item):
                self._data[i] = self._data[-1]
                self.pop()
                heapq.heapify(self._data)
                return

    def __str__(self):
        return "{}".format(list(map(lambda o: o[1], self._data)))


class PriceLevel(object):
    """
    An abstract class for price
    levels of an orderbook
    """

    def __init__(self, price):
        super(PriceLevel, self).__init__()
        self.price = price
        self._total_vol = 0
        self.store = PriorityQueue(key=lambda order: order.timestamp)

    def push(self, order):
        """
        Puts a new order into this price level

        Arguments:
            order {Order} -- an Order instance
                            (timestamp, price, volume)
        """
        self.store.push(order)
        self.total_vol += order.volume

    def pop(self, volume):
        """
        Gets a specified volume from this
        price level to symbolize execution

        Arguments:
            volume {float} -- volume to be executed/removed
        """

        filled_orders = []

        # grab target volume at this price level
        while volume > 0 and not self.is_empty():
            order = self.store.pop()

            if order.volume >= volume:
                self.total_vol -= volume
                filled_volume = volume
                order.volume -= volume
                volume = 0
            else:
                self.total_vol -= order.volume
                filled_volume = order.volume
                volume -= order.volume
                order.volume = 0

            if order.volume > 0:
                self.store.push(order)

            filled_orders.append(Order(order.timestamp,
                                       order.price,
                                       filled_volume))

        # return excess volume and all (partially) filled orders
        return volume, filled_orders, self.total_vol

    def remove(self, order):
        self.store.remove(order)
        self.total_vol -= order.volume

    def peek(self):
        return self.store.queue[0]

    def is_empty(self):
        return self.store.empty()

    @property
    def total_vol(self):
        return self._total_vol

    @total_vol.setter
    def total_vol(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid vol")
        self._total_vol = val

    def __str__(self):
        return "lll : LEVEL | price = {}, total_volume = {}".format(
            self.price, self.total_vol)


@total_ordering
class Order(object):
    """
    An order class that prioritizes
    timestamp for comparison behavior
    """

    def __init__(self, id_num, price, volume, timestamp, price_level):
        super(Order, self).__init__()
        self._id = id_num
        self._price = price
        self._volume = volume
        self._timestamp = timestamp

        price_level.push(self)
        self._price_level = price_level

    @property
    def id(self):
        return self._id

    @property
    def price_level(self):
        return self._price_level

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid timestamp")

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid price")

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        if val < 0 or val is None:
            raise ValueError("Invalid volume")
        self._volume = val

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other):
        return self.timestamp == other.timestamp

    def __str__(self):
        return "{}, {}, {}".format(self.timestamp, self.price, self.volume)
