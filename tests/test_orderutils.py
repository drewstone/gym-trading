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