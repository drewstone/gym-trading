from .orderbook import OrderBook
from .order_utils import Order, PriceLevel


class SnapshotOrderBook(OrderBook):
    """
    Orderbook reconstructor based on discretized snapshots

    Extends:
        OrderBook
    """

    def __init__(self, symbol, delta, snapshot=None):
        super(SnapshotOrderBook, self).__init__(symbol, delta)

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
            if bid not in self._bid_limits:
                self._bid_limits[bid] = PriceLevel(bid)
            order = Order(inx, bid, bid_vols[inx])
            self._bid_limits[bid].put(order)

        for inx, ask in enumerate(asks):
            if ask not in self._ask_limits:
                self._ask_limits[ask] = PriceLevel(ask)
            order = Order(inx, ask, ask_vols[inx])
            self._ask_limits[ask].put(order)

    def process_next(self, snapshot):
        """
        Processes the next snapshot to reconstruct the
        state of the orderbook over various time lengths

        Arguments:
            snapshot {Tuple} -- Tuple containing bid/ask price/vol data
        """

        # TODO: HOW CAN WE PROCESS NEW SNAPSHOTS W/O LOSING INFORMATION
        # i.e. compute some values of the diff between current and now
        self.set_snapshot(snapshot)
