import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs import simulator

if __name__ == '__main__':
    options = {
        "exchange": "GEMINI",
        "symbol": "ETHUSD",
        "data_dir": "./data/gemini",
        "data_format": "raw",
        "input_orders": 30,
        "dates": [
            20171201, 20171202, 20171203, 20171204, 20171205,
            20171206, 20171207, 20171208, 20171209, 20171210,
            20171211, 20171212, 20171213, 20171214, 20171215,
            20171216, 20171217, 20171218, 20171219, 20171221,
            20171222, 20171223, 20171224, 20171225
        ],
        "delta": 0,
        "grid_step_length": 100  # in milliseconds
    }
    sim = simulator.Simulator(options)
    while not sim.data_proc.finished:
        orderbook = sim.step(time_length=3)
