import gymnasium as gym
import numpy as np
from gymnasium import spaces

class PokemonEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0, high=1, shape(10,), dtype=np.float32)
        self.action_space = spaces.Discrete(4)

    def reset(self):
        return self._get_obs()

    def step(self, action):
        return obs, reward, done, info
    
    def _get_obs():
        return np.array([...], dtype=np.float32)