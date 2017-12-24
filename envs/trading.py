import numpy as np
from base import BaseEnv

class TradingEnv(BaseEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, security_pairs):
        for pair in security_pairs:
            self.action_space[pair] = spaces.Dict({
                positions: spaces.Discrete(3), # buy or sell for t timesteps or wait 1 timestep
                time: spaces.Box(low=0, high=10, shape=(1,)) # time length to hold
                })
        
    def _step(self, action):
        
    def _reset(self):
        
    def _render(self, mode='human', close=False):
        