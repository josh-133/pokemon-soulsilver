class Ability:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    # Battle event hooks
    def on_switch_in(self, pokemon, battle_manager):
        """Called when Pokemon with this ability enters battle"""
        pass

    def on_switch_out(self, pokemon, battle_manager):
        """Called when Pokemon with this ability leaves battle"""
        pass

    def on_damage_taken(self, attacker, defender, move, damage):
        """Called when this Pokemon takes damage"""
        pass
        
    def on_damage_dealt(self, attacker, defender, move, damage):
        """Called when this Pokemon deals damage"""
        pass

    def modify_damage(self, attacker, defender, move, damage):
        """Modify outgoing damage (like type boosts)"""
        return damage
        
    def modify_incoming_damage(self, attacker, defender, move, damage):
        """Modify incoming damage (like resistances)"""
        return damage

    def modify_attack_stat(self, pokemon, base_attack):
        """Modify the attack stat (like Guts)"""
        return base_attack
        
    def modify_defense_stat(self, pokemon, base_defense):
        """Modify the defense stat"""
        return base_defense
        
    def modify_speed_stat(self, pokemon, base_speed):
        """Modify the speed stat"""
        return base_speed

    def prevents_burn_attack_reduction(self):
        """Whether this ability prevents burn from reducing attack"""
        return False

    def prevents_status(self, status_name):
        """Whether this ability prevents a specific status"""
        return False