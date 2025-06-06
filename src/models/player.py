from pokemon import Pokemon
from typing import List

class Player:
    def __init__(self, name, team: List[Pokemon]):
        self.name = name,
        self.team = team
        self.active_index = 0
    
    def active_pokemon(self):
        return self.team[self.active_index]
    
    def has_available_pokemon(self):
        return any(p.stats.hp > 0 for p in self.team)