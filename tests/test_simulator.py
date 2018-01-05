from envs.simulator import Simulator


class MockAgent():
    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.initialized = True

    def grid(self, data):
        print("Agent: {}".format(data))
        return data


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
    m = MockAgent()
    sim.add_agent(m)

    try:
        sim.start()
    except Exception as e:
        raise e

    assert 5 == 4