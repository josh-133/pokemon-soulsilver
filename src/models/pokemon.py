import random

from .base_stats import BaseStats
from .battle_stats import BattleStats
from .ability import Ability

class Pokemon:
    def __init__(self, name, ability: Ability, base_stats: BaseStats, types, moves, level, iv, ev):
        self.name = name
        self.ability = ability
        self.base_stats = base_stats
        self.types = types
        self.moves = moves
        self.level = level
        self.iv = iv
        self.ev = ev

        self.stats = self.calculate_stats()
        self.battle_stats = BattleStats(self.stats)
        self.current_hp = self.stats["hp"]

    def generate_random_iv(self):
        return {
            "hp": random.randint(0, 31),
            "attack": random.randint(0, 31),
            "defense": random.randint(0, 31),
            "sp_attack": random.randint(0, 31),
            "sp_defense": random.randint(0, 31),
            "speed": random.randint(0, 31),
        }

    def generate_default_ev(self):
        return {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "sp_attack": 0,
            "sp_defense": 0,
            "speed": 0
        }

    def calculate_stats(self):
        def calc(stat, is_hp=False):
            base = getattr(self.base_stats, stat)
            iv = self.iv[stat]
            ev = self.ev[stat]
            if is_hp:
                return int(((2 * base + iv + ev // 4) * self.level) / 100) + self.level + 10
            else:
                return int(((2 * base + iv + ev // 4) * self.level) / 100) + 5

        return {
            "hp": calc("hp", is_hp=True),
            "attack": calc("attack"),
            "defense": calc("defense"),
            "sp_attack": calc("sp_attack"),
            "sp_defense": calc("sp_defense"),
            "speed": calc("speed"),
        }

    def is_fainted(self):
        return self.current_hp <= 0

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount):
        self.current_hp = min(self.stats["hp"], self.current_hp + amount)