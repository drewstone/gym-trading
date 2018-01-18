from ob.processor import DataProcessor
from datetime import datetime


def test_firstline_parse():
    dp = DataProcessor(data_dir="./data/gemini",
                       exchange="GEMINI", dates=[20171201])
    assert len(dp.fields) > 0
    assert dp.time == 0
    assert dp.line == 1
    assert dp.date_index == 0
    assert dp.dates == [20171201]


def test_step():
    dp = DataProcessor(data_dir="./data/gemini",
                       exchange="GEMINI", dates=[20171201])
    order = dp.next()
    assert dp.line == 2
    ts = datetime.strptime("{},{},{}".format(
        order.date, order.time, order.millis), "%Y-%m-%d,%H:%M:%S,%f")
    assert dp.time == ts
