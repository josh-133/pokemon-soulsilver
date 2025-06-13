from .pokemon import Pokemon
from typing import List

class Player:
    def __init__(self, name, is_ai, team: List[Pokemon]):
        self.name = name,
        self.is_ai = is_ai,
        self.team = team
        self.active_index = 0
    
    # return pokemon at front of party
    def active_pokemon(self):
        return self.team[self.active_index]
    
    # check if any pokemon are still alive
    def has_available_pokemon(self):
        return any(not p.is_fainted() for p in self.team)
    
    # switch a pokemon in battle
    def switch_to(self, index: int):
        if self.team[index].current_hp > 0:
            self.active_index = index
            p = self.active_pokemon()
            if p.battle_stats.status == "poison":
                p.battle_stats.badly_poisoned = False
                p.battle_stats.toxic_turns = 0