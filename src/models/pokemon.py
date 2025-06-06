import random

class BaseStats:
    def __init__(self, hp, attack, defense, sp_attack, sp_defense, speed):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed

class Ability:
    def __init__(self, name, effect, pokemon):
        self.name = name
        self.effect = effect
        self.pokemon = pokemon

class Pokemon:
    def __init__(self, name, ability, base_stats, types, moves, level, iv, ev):
        self.name = name
        self.ability = ability
        self.base_stats = base_stats
        self.types = types
        self.moves = moves
        self.level = level
        self.iv = iv
        self.ev = ev

def generate_random_iv():
    return {
        "hp": random.randint(0, 31),
        "attack": random.randint(0, 31),
        "defense": random.randint(0, 31),
        "sp_attack": random.randint(0, 31),
        "sp_defense": random.randint(0, 31),
        "speed": random.randint(0, 31),
    }

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