import random


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

        self.stats = self.calculate_stats()
        self.current_hp = self.stats["hp"]

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

    def is_fainted(self):
        return self.current_hp <= 0

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount):
        self.current_hp = min(self.stats["hp"], self.current_hp + amount)

class BaseStats:
    def __init__(self, hp, attack, defense, sp_attack, sp_defense, speed):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed

class BattleStats:
    def __init__(self, actual_stats: Pokemon.stats):
        self.max_hp = actual_stats.hp
        self.current_hp = self.max_hp
        self.battle_stats = {
            "attack": actual_stats.attack,
            "defense": actual_stats.defense,
            "sp_attack": actual_stats.sp_attack,
            "sp_defense": actual_stats.sp_defense,
            "speed": actual_stats.speed,
        }
        self.stat_modifiers = {stat: 0 for stat in self.battle_stats}

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
        return int(base * multiplier)

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

class Ability:
    def __init__(self, name, effect, pokemon):
        self.name = name
        self.effect = effect
        self.pokemon = pokemon