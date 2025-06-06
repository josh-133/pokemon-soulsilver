class Stats:
    def __init__(self, hp, attack, defense, sp_attack, sp_defense, speed):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed

class Ability:
    def __init__(self, name, effect, pokemon):
        self.name = name
        self.effect = effect
        self.pokemon = pokemon

class Pokemon:
    def __init__(self, name, ability, stats, types, moves):
        self.name = name
        self.ability = ability
        self.stats = stats
        self.types = types
        self.moves = moves