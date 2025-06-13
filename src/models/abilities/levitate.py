from .ability import Ability
from ..battle_stats import log

class Levitate(Ability):
    def __init__(self):
        super().__init__("Levitate", "Immune to Ground-type moves.")

    def modify_damage(self, attacker, defender, move, damage):
        if move.move_type.name == "GROUND":
            log(f"{defender.name}'s Levitate made it immune!")
            return 0
        return damage