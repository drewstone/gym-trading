from envs.simulator import Simulator


class MockTrader():
    def __init__(self):
        pass

    def grid(self, data):
        print(data)
        pass


def test_simulator():
    options = {
        "exchange": "GEMINI",
        "symbol": "ETHUSD",
        "data_dir": "./data/gemini",
        "data_format": "raw",
        "input_orders": 30,
        "dates": [20171201],
        "delta": 0,
        "grid_step_length": 100  # in milliseconds
    }

    sim = Simulator(options)

    sim.start()
    m = MockTrader()
    sim.add_trader(m)

    for x in range(10):
        sim.step()

    assert 5 == 4