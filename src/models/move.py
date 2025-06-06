class HitInfo:
    def __init__(self, min_hits, max_hits, min_turns, max_turns):
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.min_turns = min_turns
        self.max_turns = max_turns

class MoveEffects:
    def __init__(self, effect_chance, ailment, drain, healing, ailment_chance, flinch_chance, stat_chance):
        self.effect_chance = effect_chance
        self.ailment = ailment
        self.drain = drain
        self.healing = healing
        self.ailment_chance = ailment_chance
        self.flinch_chance = flinch_chance
        self.stat_chance = stat_chance

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
