from .ability import Ability
import random

class PoisonPoint(Ability):
    def __init__(self):
        super().__init__("Poison Point", "May poison the foe on contact")

    def on_damage_take(self, attacker, defender, move, damage):
        if move.damage_class == "Physical" and random.randint(1, 100) <= 30:
            if attacker.battle_stats.status is None:
                attacker.battle_stats.apply_status("poison")
                self.log(f"{attacker.name} was poisoned by Poison Point!")
