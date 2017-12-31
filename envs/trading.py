import csv
import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding


class TradingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    actions = {
        "BUY": 0,
        "SELL": 1,
        "WAIT": 2
    }

    def __init__(self, filename, episode_length, trading_fee=0, time_fee=0):
        """
        TradingEnv manages orderbook state, action
        execution, and reward calculation

        security_pairs <Tuple<String,String>> consisting of pair
        identifier and accompanying data file for training and testing
        """

        # Filename for historical data
        self.ob_filename = filename

        # Actions spaces
        self._action_space = spaces.Tuple(spaces.Discrete(3),
                                          spaces.Box(low=0,
                                                     high=10,
                                                     shape=(1,)))
        self._observation_space = spaces.Box(-float(9999999999),
                                             float(9999999999),
                                             shape=(1,))

        self._first_render = True
        self._time = 0
        self._position = 0
        self._episode_length = episode_length
        self._trading_fee = trading_fee
        self._time_fee = time_fee

        self._reset()

    def _step(self, action):
        assert self.action_space.contains(action)
        reward = -1
        position_action = action['position']
        horizon_length = action['time']

        # Ensure we aren't mid-action (i.e FREEZE POLICY)
        if self.time_horizon == 0:

            self.stepper = 0

            if action['position'] == 0:  # BUY
                self.time_horizon = horizon_length
                continue
            elif action['position'] == 1:  # SELL
                self.time_horizon = horizon_length
                continue
            elif action['position'] == 2:  # WAIT
                self.time_horizon = 0
                continue

            self.state = self.orderbook.process_order()

                # Game over logic
        try:
            self._prices_history.append(self._data_generator.next())
        except StopIteration:
            done = True
            info['status'] = 'No more data.'
        if self._iteration >= self._episode_length:
            done = True
            info['status'] = 'Time out.'
        if self._closed_plot:
            info['status'] = 'Closed plot'

        return self.state, reward, done, {}

    def _reset(self):
        self.position_action = None
        self.time_horizon = 10
        self.OrderBookIterator(self.ob_filename)
        return self._get_obs()

    def _get_obs(self):
        if self.position_action is None:
            return self.np_random.choice()
        else:
            return self.position_action

    def _render(self, mode='human', close=False):
        return

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

# if __name__ == '__main__':
#     filename = "./data/GDAX.ETHUSD.2017-12-22.csv"
#     t = TradingEnv(filename)
#     print(t.orderbook.bid)
