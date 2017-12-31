from .orderbook import OrderBook


class OrderBookWrapper(OrderBook):
    """A wrapper for a limit order book for various data formats

    The orderbook wrapper should format various data sources
    to properly place orders into the limit order book. The various
    data source we are interested in are orderbook snapshots as
    fixed time intervals or raw data in the format of individual orders

    Extends:
        OrderBook
    """

    def __init__(self, symbol, delta, data_type, input_data):
        super(OrderBookWrapper, self).__init__(symbol, delta)
        self.set_state(input_data)

    def set_state(self, snapshot):
        """
        Reconstructs orderbook state from a given snapshot

        Used to initialize the orderbook state

        Arguments:
            snapshot {tuple} -- tuple containing bid/ask price/vol data
        """
        bids, bid_vols, asks, ask_vols = snapshot

        for inx, bid in enumerate(bids):
            self.limit("BID", bid, bid_vols[inx])

        for inx, ask in enumerate(asks):
            self.limit("ASK", ask, ask_vols[inx])

    def process_next(self, snapshot):
        """
        Processes the next snapshot to reconstruct the
        state of the orderbook over various time lengths

        Arguments:
            snapshot {tuple} -- tuple containing bid/ask price/vol data
        """

        # TODO: HOW CAN WE PROCESS NEW SNAPSHOTS W/O LOSING INFORMATION
        # i.e. compute some values of the diff between current and now
        self.set_state(snapshot)
