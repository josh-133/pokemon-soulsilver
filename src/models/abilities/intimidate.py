from .ability import Ability

class Intimidate(Ability):
    def __init__(self):
        super().__init__("Intimidate", "Lowers the foe's Attack stat.")
    
    def on_switch_in(self, pokemon, battle_manager):
        """Lower opponent's attack when this Pokemon enters battle"""
        # Determine opponent
        if battle_manager.player.active_pokemon() == pokemon:
            opponent = battle_manager.opponent.active_pokemon()
            owner_name = battle_manager.player.name
        else:
            opponent = battle_manager.player.active_pokemon()
            owner_name = battle_manager.opponent.name
        
        # Lower opponent's attack by 1 stage
        opponent.battle_stats.modify_stat("attack", -1)
        
        if hasattr(battle_manager, 'log'):
            battle_manager.log(f"{owner_name}'s {pokemon.name}'s Intimidate lowered {opponent.name}'s Attack!")
    
    def immune_to_intimidate(self):
        """Some abilities make Pokemon immune to Intimidate"""
        return False