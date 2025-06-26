import gymnasium as gym
import numpy as np
import random
from gymnasium import spaces
from models.battle_manager import BattleManager
from models.player import Player
from models.type_chart import get_type_multiplier
from data.loaders import load_pokemon, get_move_lookup

class PokemonEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.move_lookup = get_move_lookup()

        # 4 possible moves
        self.action_space = spaces.Discrete(4)

        # Observation: [player_hp, opp_hp, 4 move powers, 4 move pp ratios, player_speed, opp_speed]
        # The agent will receive a 12-dimensional vector of continuous values. Each value will be a floating-point number between 0 and 1.
        self.observation_space = spaces.Box(low=0, high=1, shape=(12,), dtype=np.float32)

        self._setup_battle()

    def _setup_battle(self):
        self.player = Player("AI", is_ai=True, pokemon_team=[load_pokemon("pikachu", self.move_lookup)])
        self.opponent = Player("Opponent AI", is_ai=True, pokemon_team=[load_pokemon("charmander", self.move_lookup)])

        self.battle = BattleManager(self.player, self.opponent)

    def reset(self):
        self._setup_battle()
        return self._get_obs()

    def step(self, action):
        # Make sure action is valid
        moves = self.player.active_pokemon().moves
        if action >= len(moves):
            action = random.randint(0, len(moves) - 1)

        chosen_move = moves[action]
        player_action = self.battle.make_player_action("move", move=chosen_move)
        
        opponent_moves = self.opponent.active_pokemon().moves
        best_move = opponent_moves.moves[0]
        best_score = -float("inf")

        for move in opponent_moves:
            if self.opponent.active_pokemon().battle_stats.pp.get(move.name, 0) <= 0:
                continue

            stab = 1.5 if move.move_type in self.opponent.active_pokemon().types else 1.0
            effectiveness = 1.0
            for t in self.player.active_pokemon().types:
                effectiveness *= get_type_multiplier(move.move_type, t)
                
            score = (move.power or 0) * stab * effectiveness

            if score > best_score:
                best_move = move
        
        opponent_action = self.battle.make_player_action("move", move=best_move)

        # --- Reward shaping block ---
        prev_opp_hp = self.opponent.active_pokemon().battle_stats.current_hp
        prev_player_hp = self.player.active_pokemon().battle_stats.current_hp

        self.battle.take_turn(player_action, opponent_action)

        post_opp_hp = self.opponent.active_pokemon().battle_stats.current_hp
        post_player_hp = self.player.active_pokemon().battle_stats.current_hp

        damage_dealt = max(0, prev_opp_hp - post_opp_hp)
        damage_taken = max(0, prev_player_hp - post_player_hp)

        reward = (damage_dealt / self.opponent.active_pokemon().stats["hp"])
        reward -= 0.2 * (damage_taken / self.player.active_pokemon().stats["hp"])

        done = False

        if self.opponent.active_pokemon().is_fainted():
            reward += 1.0
            done = True

        if self.player.active_pokemon().is_fainted():
            reward -= 1.0
            done = True 

        return self._get_obs(), reward, done, {}
    
    def _get_obs(self):
        p = self.player.active_pokemon()
        o = self.opponent.active_pokemon()

        obs = [
            p.battle_stats.current_hp / p.stats["hp"],
            o.battle_stats.current_hp / o.stats["hp"]
        ]

        for i in range(4):
            if i < len(p.moves):
                move = p.moves[i]
                power = (move.power or 0) / 100
                pp_ratio = p.battle_stats.pp.get(move.name, 0) / (move.pp or 1)
            else:
                power = 0
                pp_ratio = 0
            obs.append(power)
            obs.append(pp_ratio)

        # Add speed (normalised)
        obs.append(p.stats["speed"] / 200)
        obs.append(o.stats["speed"] / 200)

        return np.array(obs, dtype=np.float32)