import time
from datetime import datetime as dt
from ob.order_utils import Order, PriceLevel
from ob.orderbook import OrderBook


def test_limit_orders():
    ob = OrderBook("ETHUSD")
    for i in range(3):
        ob.limit("BID", 10, 10)

    assert ob.bid == 10
    assert ob.bid_vol == 30

    for i in range(3):
        ob.limit("ASK", 11, 10)

    assert ob.ask == 11
    assert ob.ask_vol == 30


def test_limit_execution():
    ob = OrderBook("ETHUSD")
    for i in range(3):
        ob.limit("BID", 10, 10)
        ob.limit("ASK", 10, 10)

    assert ob.bid == 0
    assert ob.bid_vol == 0
    assert ob.ask == float(9999999999)
    assert ob.ask_vol == 0


def test_limit_market_execution():
    ob = OrderBook("ETHUSD")
    for i in range(3):
        ob.limit("BID", i + 1, 1)

    ob.limit("ASK", 4, 1)
    ob.limit("ASK", 4, 1)
    ob.limit("ASK", 5, 1)

    assert ob.bid == 3
    assert ob.bid_vol == 1
    assert ob.ask == 4
    assert ob.ask_vol == 2

    ob.limit("BID", 4, 2)

    assert ob.bid == 3
    assert ob.bid_vol == 1
    assert ob.ask == 5
    assert ob.ask_vol == 1
