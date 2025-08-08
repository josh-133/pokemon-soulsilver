from models.type_chart import get_type_multiplier
from models.types import Type
import logging
import random

class HitInfo:
    def __init__(self, min_hits, max_hits, min_turns, max_turns):
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.min_turns = min_turns
        self.max_turns = max_turns

class MoveEffects:
    def __init__(self, effect_chance, ailment, drain, healing, ailment_chance, flinch_chance, stat_chance, stat_changes, is_badly_poisoning=False):
        self.effect_chance = effect_chance
        self.ailment = ailment
        self.drain = drain
        self.healing = healing
        self.ailment_chance = ailment_chance
        self.flinch_chance = flinch_chance
        self.stat_chance = stat_chance
        self.stat_changes = stat_changes
        self.is_badly_poisoning = is_badly_poisoning

class Move:
    def __init__(self, name, accuracy, pp, priority, power, damage_class, crit_rate, target, category, move_type, hit_info, effects_info):
        self.name = name
        self.accuracy = accuracy
        self.pp = pp
        self.priority = priority
        self.power = power
        self.damage_class = damage_class
        self.crit_rate = crit_rate
        self.target = target
        self.category = category
        self.move_type = move_type
        self.hit_info = hit_info
        self.effects_info = effects_info



    def calculate_critical_hit_chance(self, attacker):
        crit_stage = self.crit_rate or 0
        
        # Generation 4 critical hit rates
        crit_rates = {
            0: 1/16,   # 6.25% (normal)
            1: 1/8,    # 12.5% (high crit moves like Slash)
            2: 1/4,    # 25% (Focus Energy + high crit move)
            3: 1/3,    # 33.3%
            4: 1/2,    # 50%
        }
        
        # Cap at stage 4
        crit_stage = min(crit_stage, 4)
        crit_chance = crit_rates.get(crit_stage, 1/16)
        
        random_roll = random.random()
        is_crit = random_roll < crit_chance
        
        logging.info(f"Critical hit check for {self.name}: stage={crit_stage}, chance={crit_chance:.4f}, roll={random_roll:.4f}, result={is_crit}")
        
        return is_crit

    def apply_damage(self, attacker, defender):
        logging.info(f"Apply damage called for move: {self.name}")
        if self.power is None or self.damage_class == "status":
            logging.info(f"Move {self.name} is status move or has no power, returning 0 damage")
            return 0, False
        
        # Check for critical hit
        is_critical = self.calculate_critical_hit_chance(attacker)
        logging.info(f"Critical hit result for {self.name}: {is_critical}")
        
        # Get relevant stats - for crits, ignore stat changes that would be disadvantageous
        if self.damage_class == "physical":
            if is_critical:
                # Critical hits ignore negative attack stages and positive defense stages
                attack_mod = max(0, attacker.battle_stats.stat_modifiers.get("attack", 0))
                defense_mod = min(0, defender.battle_stats.stat_modifiers.get("defense", 0))
                attack = attacker.battle_stats.battle_stats["attack"] * attacker.battle_stats.get_stage_multiplier(attack_mod)
                defense = defender.battle_stats.battle_stats["defense"] * defender.battle_stats.get_stage_multiplier(defense_mod)
            else:
                attack = attacker.battle_stats.get_effective_stat("attack")
                defense = defender.battle_stats.get_effective_stat("defense")
        else:
            if is_critical:
                # Critical hits ignore negative sp_attack stages and positive sp_defense stages
                sp_attack_mod = max(0, attacker.battle_stats.stat_modifiers.get("sp_attack", 0))
                sp_defense_mod = min(0, defender.battle_stats.stat_modifiers.get("sp_defense", 0))
                attack = attacker.battle_stats.battle_stats["sp_attack"] * attacker.battle_stats.get_stage_multiplier(sp_attack_mod)
                defense = defender.battle_stats.battle_stats["sp_defense"] * defender.battle_stats.get_stage_multiplier(sp_defense_mod)
            else:
                attack = attacker.battle_stats.get_effective_stat("sp_attack")
                defense = defender.battle_stats.get_effective_stat("sp_defense")

        # Apply STAB bonus
        stab = 1.5 if self.move_type in [t.value for t in attacker.types] else 1.0

        logging.info(f"MOVE TYPE: {self.move_type}, ATTACKER TYPES: {attacker.types}")
        # Apply type effectiveness
        type_multiplier = 1.0
        for t in defender.types:
            type_effect = get_type_multiplier(self.move_type, t)
            logging.info(f"{self.move_type} vs {t} = {type_effect}")
            type_multiplier *= type_effect

        # Calculate final damage
        level = attacker.level
        power = self.power
        damage = (((2 * level / 5 + 2) * power * attack / defense) / 50 + 2)
        damage = int(damage * stab * type_multiplier)
        
        # Apply critical hit multiplier
        if is_critical:
            damage = int(damage * 2)

        return max(1, damage), is_critical