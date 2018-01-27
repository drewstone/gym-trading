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







# OLD STUFF

# orderbooks = sim.initialize_raw()

# date_strs = []
# for date in options["dates"]:
#     d_str = str(date)
#     d_str = d_str[:4] + "-" + d_str[4:6] + "-" + d_str[6:]
#     date_strs.append(d_str)

# cutoff_timestamp = lambda date: datetime.strptime(
#     "{} 23:59:55".format(date), "%Y-%m-%d %H:%M:%S")

# with open('./data/gemini-snapshot.csv', 'a') as f:
#     for inx, date in enumerate(options["dates"]):
#         ob_str = [str(v) for v in orderbooks[date].to_vec()]
#         f.write("{},{}\n".format(",".join(ob_str),
#                                  orderbooks[date].last_datetime))

#         while True:
#             try:
#                 orderbook = sim.next(date=date, time_length=3)
#                 ob_str = [str(v) for v in orderbooks[date].to_vec()]
#                 f.write("{},{}\n".format(",".join(ob_str),
#                                          orderbooks[date].last_datetime))
#             except StopIteration:
#                 sim.next_date()
#                 break
#     f.close()
