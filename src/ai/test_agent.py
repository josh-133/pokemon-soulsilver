# test_agent.py
# This script evaluates a trained model over multiple simulated battles,
# logs win/loss statistics, and plots performance metrics.

from stable_baselines3 import PPO
from ai.pokemon_env import PokemonEnv
import csv
import os
import logging
import matplotlib.pyplot as plt

model = PPO.load("src/ai/trained_model_selfplay")

NUM_BATTLES = 100
wins = 0
losses = 0
draws = 0
total_turns = 0
total_reward = 0

results = []

for i in range(1, NUM_BATTLES + 1):
    env = PokemonEnv(opponent_model=model)
    obs, _ = env.reset()
    done = False
    turns = 0

    while not done:
        turns += 1
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
    
    total_turns += turns
    total_reward += reward

    if reward > 0:
        wins += 1
        result = "Win"
    elif reward < 0:
        losses += 1
        result = "Loss"
    else:
        draws += 1
        result = "Draw"

    logging.info(f"Battle {i:03} finished in {turns} turns -> {result}")
    results.append((i, turns, reward, result))

csv_path = os.path.join(os.path.dirname(__file__), "evaluation_results.csv")
with open(csv_path, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow((["Battle", "Turns", "Reward", "Result"]))
    writer.writerows(results)

# Final stats
logging.info("\n Evaluation Summary:")
logging.info(f"Total Battles: {NUM_BATTLES}")
logging.info(f"Wins   : {wins}")
logging.info(f"Losses : {losses}")
logging.info(f"Draws  : {draws}")
logging.info(f"Win Rate     : {wins / NUM_BATTLES:.2%}")
logging.info(f"Loss Rate    : {losses / NUM_BATTLES:.2%}")
logging.info(f"Avg Turns    : {total_turns / NUM_BATTLES:.2f}")
logging.info(f"Avg Reward   : {total_reward / NUM_BATTLES:.2f}")

# Plotting
labels = ['Wins', 'Losses', 'Draws']
sizes = [wins, losses, draws]
colors = ['green', 'red', 'gray']
plt.figure(figsize=(10, 5))

# Pie chart
plt.subplot(1, 2, 1)
plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
plt.axis('equal')
plt.title("Battle Outcomes")

# Reward trend
plt.subplot(1, 2, 2)
battle_numbers = [r[0] for r in results]
rewards = [r[2] for r in results]
plt.plot(battle_numbers, rewards, marker='o', linestyle='-', color='blue')
plt.xlabel("Battle Number")
plt.ylabel("Reward")
plt.title("Reward per Battle")

plt.tight_layout()
plt.show()