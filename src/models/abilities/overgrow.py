from .ability import Ability

class Overgrow(Ability):
    def __init__(self):
        super().__init__("Overgrow", "Powers up Grass moves when HP is low.")
    
    def modify_damage(self, attacker, defender, move, damage):
        """Boost Grass moves by 50% when HP is below 1/3"""
        if (move.move_type.value == "grass" and 
            attacker.battle_stats.current_hp <= attacker.battle_stats.max_hp // 3):
            return int(damage * 1.5)
        return damage