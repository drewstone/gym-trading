from ob.processor import DataProcessor


def test_firstline_parse():
    dp = DataProcessor(data_dir="./data/gemini", dates=[20171201])
    assert 5 == 4
    pass