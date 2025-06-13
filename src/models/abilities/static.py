from .ability import Ability
import random

class Static(Ability):
    def __init__(self):
        super().__init__("Static", "May paralyze on contact.")

    def on_damage_take(self, attacker, defender, move, damage):
        if move.damage_class == "Physical" and random.randint(1, 100) <= 30:
            attacker.battle_stats.apply_status("paralysis")
            self.log("f{attacker.name} was paralyzed by Static!")