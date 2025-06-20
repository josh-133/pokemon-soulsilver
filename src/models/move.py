from models.type_chart import get_type_multiplier
from models.types import Type

class HitInfo:
    def __init__(self, min_hits, max_hits, min_turns, max_turns):
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.min_turns = min_turns
        self.max_turns = max_turns

class MoveEffects:
    def __init__(self, effect_chance, ailment, drain, healing, ailment_chance, flinch_chance, stat_chance, is_badly_poisoning=False):
        self.effect_chance = effect_chance
        self.ailment = ailment
        self.drain = drain
        self.healing = healing
        self.ailment_chance = ailment_chance
        self.flinch_chance = flinch_chance
        self.stat_chance = stat_chance
        self.is_badly_poisoning = is_badly_poisoning

class Move:
    def __init__(self, name, accuracy, pp, priority, power, damage_class, crit_rate, category, move_type, hit_info, effects_info):
        self.name = name
        self.accuracy = accuracy
        self.pp = pp
        self.priority = priority
        self.power = power
        self.damage_class = damage_class
        self.crit_rate = crit_rate
        self.category = category
        self.move_type = move_type
        self.hit_info = hit_info
        self.effects_info = effects_info



    def apply_damage(self, attacker, defender):
        if self.power is None or self.damage_class == "status":
            return 0
        
        # Get relevant stats
        if self.damage_class == "physical":
            attack = attacker.battle_stats.get_effective_stat("attack")
            defense = defender.battle_stats.get_effective_stat("defense")
        else:
            attack = attacker.battle_stats.get_effective_stat("sp_attack")
            defense = defender.battle_stats.get_effective_stat("sp_defense")

        # Apply STAB bonus
        stab = 1.5 if self.move_type in attacker.types else 1.0

        # Apply type effectiveness
        type_multiplier = 1.0
        for t in defender.types:
            type_multiplier *= get_type_multiplier(self.move_type, t)

        # Calculate final damage
        level = attacker.level
        power = self.power
        damage = (((2 * level / 5 + 2) * power * attack / defense) / 50 + 2)
        damage = int(damage * stab * type_multiplier)

        return max(1, damage)