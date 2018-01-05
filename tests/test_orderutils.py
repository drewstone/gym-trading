from datetime import datetime as dt
from ob.order_utils import Order, PriceLevel


def test_order():
    price = 5.0
    volume = 1
    p = PriceLevel(price)
    o = Order(0, 5.0, 1, dt.now(), p)

    assert o.price == price
    assert o.volume == volume
    assert o.price_level == p

    assert o.price_level.total_vol == volume
    assert p.total_vol == volume


def test_pricelevel_change():
    price = 5.0
    volume = 1
    p = PriceLevel(price)
    o1 = Order(0, price, volume, dt.now(), p)
    o2 = Order(1, price, volume, dt.now(), p)

    assert o1.price_level.total_vol == 2
    assert o2.price_level.total_vol == 2
    assert p.total_vol == 2

    o2.price_level.remove(o2)
    assert p.total_vol == 1
    assert o1.price_level.total_vol == 1
    assert o2.price_level.total_vol == 1
    assert o1.price_level == o2.price_level == p

    assert not p.contains(o2)
    assert p.contains(o1)
    assert o1.price_level.contains(o1)
    assert not o1.price_level.contains(o2)
    assert o2.price_level.contains(o1)
    assert not o2.price_level.contains(o2)


def test_many_changes():
    price = 5.0
    volume = 1
    p = PriceLevel(price)

    orders = []
    for i in range(10):
        orders.append(Order(i, price, volume, dt.now(), p))

    assert p.total_vol == 10
    for i in range(10):
        p.remove(orders[i])
        assert not p.contains(orders[i])

    assert p.total_vol == 0
