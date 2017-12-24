import csv
import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding

class OrderBookIterator(object):
    """docstring for Order"""
    def __init__(self, filename):
        super(Order, self).__init__()
        self.read_csv(filename)

    def read_csv(self, filename):
        orderbooks = csv.reader(filename, delimiter=',')


    @property
    def bid(self):
        return self._bid

    @bid.setter
    def bid(self, val):
        if bid < 0:
            raise ValueError("Invalid bid")
        self._bid = val

    @property
    def ask(self):
        return self._ask

    @ask.setter
    def ask(self, val):
        if ask > float(9999999999):
            raise ValueError("Invalid ask")
        self._ask = val

class TradingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, filename):
        """
        TradingEnv manages orderbook state, action
        execution, and reward calculation

        security_pairs <Tuple<String,String>> consisting of pair
        identifier and accompanying data file for training and testing
        """

        self.orderbook = OrderBookIterator(filename)
        self.action_space = spaces.Dict({
            positions: spaces.Discrete(3), # buy or sell for t timesteps or wait 1 timestep
            time: spaces.Box(low=0, high=10, shape=(1,)) # time length to hold
            })
        
    def _step(self, action):
        return
    def _reset(self):
        return

    def _render(self, mode='human', close=False):
        return

if __name__ == '__main__':
    filename = "./data/GDAX.ETHUSD.2017-12-22.csv"
    t = TradingEnv(filename)