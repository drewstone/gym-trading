from datetime import datetime as dt
from ob.order_utils import Order, PriceLevel
from ob.ordertree import Tree


def test_tree_creation():
    t = Tree()
    assert t.volume == 0
    assert t.max_price is None
    assert t.min_price is None


def test_tree_insert():
    t = Tree()
    price = 5.0
    t.create_price(price)

    assert t.max_price == 5.0
    assert t.min_price == 5.0
    assert len(t.price_map.keys()) == 1
    assert t.price_exists(price)
    assert not t.price_exists(price + 1)


def test_tree_orders():
    t = Tree()
    price = 5.0
    volume = 1
    id_num = 0
    t.insert_order(id_num, price, volume)

    assert t.max_price == 5.0
    assert t.min_price == 5.0
    assert len(t.price_map.keys()) == 1
    assert t.price_exists(price)
    assert not t.price_exists(price + 1)
    assert t.order_exists(0)

    assert t.volume == 1
    o = t.get_order(id_num)
    assert o.timestamp < dt.now()
    assert o.volume == 1
    assert o.price == price
    assert o.id == id_num


def test_tree_removal():
    t = Tree()
    price = 5.0
    volume = 1
    id_num = 0
    t.insert_order(id_num, price, volume)
    t.remove_order_by_id(id_num)

    assert t.volume == 0
    assert not t.order_exists(id_num)
    assert not t.price_exists(price)
