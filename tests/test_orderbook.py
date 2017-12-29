import sys
import time
from datetime import datetime as dt
sys.path.append('../')

try:
    import gym_trading as gt
    from gt.envs.ob.order_utils import Order, PriceLevel
    from g.envs.ob.orderbook import OrderBook
except Exception as e:
    import gym_trading as gt
    Order = gt.envs.ob.order_utils.Order
    PriceLevel = gt.envs.ob.order_utils.PriceLevel
    OrderBook = gt.envs.ob.orderbook.OrderBook


def test_order():
    o = Order(dt.now(), 10, 10)
    time.sleep(1)
    o2 = Order(dt.now(), 10, 10)
    assert o.price == 10
    assert o.volume == 10
    assert o < o2


def test_pricelevel():
    level = PriceLevel(10)
    for i in range(3):
        timestamp = dt.now()
        if i == 0:
            ts = timestamp
        o = Order(timestamp, 10, 10)
        time.sleep(1)
        level.put(o)

    assert level.total_vol == 30
    assert level.price == 10
    assert level.peek().timestamp == ts


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
