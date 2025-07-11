from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from ai.pokemon_env import PokemonEnv
import logging

logging.basicConfig(
    filename="training_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Step 1: Create initial environment (no opponent model yet)
env = DummyVecEnv([lambda: PokemonEnv(opponent_model=None)])

# Step 2: Create PPO model
model = PPO("MlpPolicy", env, verbose=1)

# Step 3: Rewrap the environment with the model as its opponent
# Note: We use lambda again to recreate envs with opponent model set
self_play_env = DummyVecEnv([lambda: PokemonEnv(opponent_model=model)])

# Step 4: Set new environment and begin training
model.set_env(self_play_env)
model.learn(total_timesteps=100_000)

model.save("src/ai/trained_model_selfplay")

logging.info("Training complete. Model saved to ai/trained_model_selfplay.zip")

# Test the trained model against itself
test_env = PokemonEnv(opponent_model=model)
obs, _ = test_env.reset()
done = False

step_count = 0
logging.info("\n Starting test battle (self-play):")

while not done:
    step_count += 1
    action, _ = model.predict(obs, deterministic=True)

    # Save previous HP to see damage
    player = test_env.player.active_pokemon()
    opponent = test_env.opponent.active_pokemon()
    prev_hp_opp = opponent.battle_stats.current_hp
    prev_hp_player = player.battle_stats.current_hp

    obs, reward, terminated, truncated, _ = test_env.step(action)
    done = terminated or truncated
    
    damage_to_opp = prev_hp_opp - opponent.battle_stats.current_hp
    damage_to_player = prev_hp_player - player.battle_stats.current_hp

    logging.info(f"\nTurn {step_count}:")
    logging.info(f"{player.name} dealt {damage_to_opp} damage to {opponent.name}")
    logging.info(f"{opponent.name} dealt {damage_to_player} damage to {player.name}")
    logging.info(f"Status: {player.name} HP = {player.battle_stats.current_hp}, {opponent.name} HP = {opponent.battle_stats.current_hp}")

    if reward > 0:
        logging.info("Agent won the battle!")
    elif reward < 0:
        logging.info("Agent lost the battle!")
    else:
        logging.info("It's a draw!")
    logging.info(f"Total turns: {step_count}")
    logging.info(f"Final reward: {reward}")
    
    test_env.render()