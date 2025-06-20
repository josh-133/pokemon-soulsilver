import random
import requests
import io
import pygame

from .base_stats import BaseStats
from .battle_stats import BattleStats
from .abilities.ability import Ability

def load_sprite(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = response.content
        return pygame.image.load(io.BytesIO(image_data)).convert_alpha()
    except Exception as e:
        print(f"Failed to load sprite from {url}: {e}")
        return None

class Pokemon:
    def __init__(self, name, ability: Ability, base_stats: BaseStats, types, moves, level, iv, ev, front_sprite=None, back_sprite=None):
        self.name = name
        self.ability = ability
        self.base_stats = base_stats
        self.types = types
        self.moves = moves
        self.level = level
        self.iv = iv
        self.ev = ev
        self.front_sprite = front_sprite
        self.back_sprite = back_sprite
        
        self.stats = self.calculate_stats()
        self.battle_stats = BattleStats(self)

    @staticmethod
    def generate_random_iv():
        return {
            "hp": random.randint(0, 31),
            "attack": random.randint(0, 31),
            "defense": random.randint(0, 31),
            "sp_attack": random.randint(0, 31),
            "sp_defense": random.randint(0, 31),
            "speed": random.randint(0, 31),
        }

    @staticmethod
    def generate_default_ev():
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
        return self.battle_stats.is_fainted()

    def take_damage(self, amount):
        self.battle_stats.take_damage(amount)

    def heal(self, amount):
        self.battle_stats.heal(amount)