class Ability:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def on_switch_in(self, pokemon, battle_manager):
        pass

    def on_damage_take(self, attacker, defender, move, damage):
        pass

    def modify_damage(self, attacker, defender, move, damage):
        return damage