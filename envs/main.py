import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from envs import simulator

if __name__ == '__main__':
    options = {
        "exchange": "GEMINI",
        "symbol": "ETHUSD",
        "data_dir": "./data/gemini",
        "data_format": "raw",
        "input_orders": 30,
        "dates": [20171201, 20171202],
        "delta": 0,
        "grid_step_length": 100  # in milliseconds
    }
    sim = simulator.Simulator(options)
    while not sim.is_finished():
        ob = sim.next()
    print(sim.orderbook.last_datetime, sim.orderbook.state())