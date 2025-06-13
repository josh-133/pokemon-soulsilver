from models.type_chart import get_type_multiplier
from models.types import Type
from models.battle_manager import log

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

        def create_move_from_data(move_data):
            effects_info = MoveEffects(
                effect_chance = move_data["effect_chance"],
                ailment = move_data["ailment"],
                drain = move_data["drain"],
                healing = move_data["healing"],
                ailment_chance = move_data["ailment_chance"],
                flinch_chance = move_data["flinch_chance"],
                stat_chance = move_data["stat_chance"],
                is_badly_poisoning = move_data["is_badly_poisoning"],
            )

            if move_data["name"].lower() == "toxic":
                effects_info.is_badly_poisoning = True
            
            hit_info = HitInfo(
                min_hits  = move_data["min_hits"],
                max_hits  = move_data["max_hits"],
                min_turns = move_data["min_turns"],
                max_turns = move_data["max_turns"],
            )

            move = Move(
                name = move_data["name"],
                accuracy = move_data["accuracy"],
                pp = move_data["pp"],
                priority = move_data["priority"],
                power = move_data["power"],
                damage_class = move_data["damage_class"],
                crit_rate = move_data["crit_rate"],
                category = move_data["category"],
                move_type = move_data["move_type"],
                hit_info = hit_info,
                effects_info = effects_info,
            )

            return move



        def apply_damage(move, attacker, defender):
            log(f"{attacker.active_pokemon().name} used {move.name}!")

            if move.power is None or move.damage_class == "status":
                return 0
            
            # Get relevant stats
            if move.damage_class == "physical":
                attack = attacker.battle_stats.get_effective_stat("attack")
                defense = defender.battle_status.get_effective_stat("defense")
            else:
                attack = attacker.battle_stats.get_effective_stat("sp_attack")
                defense = defender.battle_status.get_effective_stat("sp_defense")

            # Apply STAB bonus
            stab = 1.5 if move.move_type in attacker.types else 1.0

            # Apply type effectiveness
            type_multiplier = 1.0
            for t in defender.types:
                type_multiplier *= get_type_multiplier(move.move_type, t)

                if type_multiplier >= 2:
                    log("It's super effective!")
                elif type_multiplier < 1:
                    log("Not very effective...")

            # Calculate final damage
            level = attacker.level
            power = move.power
            damage = (((2 * level / 5 + 2) * power * attack / defense) / 50 + 2)
            damage = int(damage * stab * type_multiplier)

            return max(1, damage)