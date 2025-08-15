from .ability import Ability

class Guts(Ability):
    def __init__(self):
        super().__init__("Guts", "Boosts Attack when statused.")
    
    def modify_attack_stat(self, pokemon, base_attack):
        """Increase attack by 50% when statused"""
        if pokemon.battle_stats.status is not None:
            return int(base_attack * 1.5)
        return base_attack
    
    def prevents_burn_attack_reduction(self):
        """Guts prevents burn from reducing physical attack"""
        return True