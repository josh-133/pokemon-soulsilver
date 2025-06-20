from stable_baselines3 import PPO
from pokemon_env import PokemonEnv

env = PokemonEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)
model.save("ai/trained_model")