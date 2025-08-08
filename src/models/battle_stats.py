import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .pokemon import Pokemon

class BattleStats:
    def __init__(self, pokemon: "Pokemon",):
        self.max_hp = pokemon.stats["hp"]
        self.current_hp = self.max_hp
        self.battle_stats = {
            "attack": pokemon.stats["attack"],
            "defense": pokemon.stats["defense"],
            "sp_attack": pokemon.stats["sp_attack"],
            "sp_defense": pokemon.stats["sp_defense"],
            "speed": pokemon.stats["speed"],
            "accuracy": 0,
            "evasion": 0,
        }
        self.status = None
        self.badly_poisoned = False
        self.toxic_turns = 0
        self.sleep_turns = 0
        self.pp = {move.name: move.pp for move in pokemon.moves}
        self.stat_modifiers = {stat: 0 for stat in self.battle_stats}

    def is_fainted(self):
        return self.current_hp <= 0
    
    def apply_status(self, condition: str):
        if self.status is None:
            self.status = condition

    def set_pp(self, move_name: str, max_pp: int):
        self.pp[move_name] = max_pp

    def use_pp(self, move_name: str):
        print(f"Using PP for: {move_name}")
        if self.pp.get(move_name, 0) > 0:
            self.pp[move_name] -= 1
        else:
            raise ValueError(f"No PP left for move {move_name}.")
        
    def has_pp(self, move_name: str):
        return self.pp.get(move_name, 0) > 0
    
    def apply_stat_change(self, stat_name: str, amount: int):
        self.modify_stat(stat_name, amount)

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)
        logging.info(f"{self.current_hp} / {self.max_hp}")

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def modify_stat(self, stat_name: str, stat_change: int, ):
        if stat_name not in self.stat_modifiers:
            return
        
        current_stage = self.stat_modifiers[stat_name]
        new_stage = max(-6, min(6, current_stage + stat_change))
        self.stat_modifiers[stat_name] = new_stage

    def get_effective_stat(self, stat_name: str):
        base = self.battle_stats[stat_name]
        stage = self.stat_modifiers[stat_name]
        multiplier = self.get_stage_multiplier(stage)
        stat_value = int(base * multiplier)
        
        # Apply status effects
        if stat_name == "speed" and self.status == "paralysis":
            # Paralysis reduces speed to 25% of normal
            stat_value = int(stat_value * 0.25)
            
        return stat_value

    def get_stage_multiplier(self, stage: int) -> float:
        if stage >= 0:
            return (2 + stage) / 2
        else:
            return 2 / (2 - stage)
        
    def get_acc_eva_multiplier(self, stage) -> float:
        if stage >= 0:
            return (3 + stage) / 3
        else:
            return 3 / (3 - stage)