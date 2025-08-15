"""Centralized ability creation and management"""
from typing import Dict, Type
from .ability import Ability
from .static import Static
from .poison_point import PoisonPoint
from .levitate import Levitate
from .guts import Guts
from .overgrow import Overgrow
from .intimidate import Intimidate

class AbilityFactory:
    """Factory for creating abilities by name"""
    
    _abilities: Dict[str, Type[Ability]] = {
        "static": Static,
        "poison-point": PoisonPoint,
        "levitate": Levitate,
        "guts": Guts,
        "overgrow": Overgrow,
        "intimidate": Intimidate,
    }
    
    @classmethod
    def create_ability(cls, ability_name: str) -> Ability:
        """Create an ability instance by name"""
        if not ability_name:
            return Static()  # Default ability
            
        # Normalize name (lowercase, replace spaces with hyphens)
        normalized_name = ability_name.lower().replace(" ", "-")
        
        ability_class = cls._abilities.get(normalized_name)
        if ability_class:
            return ability_class()
        else:
            # Return a generic ability with the name for unknown abilities
            return Ability(ability_name.title(), f"Unknown ability: {ability_name}")
    
    @classmethod
    def register_ability(cls, name: str, ability_class: Type[Ability]):
        """Register a new ability class"""
        normalized_name = name.lower().replace(" ", "-")
        cls._abilities[normalized_name] = ability_class
    
    @classmethod
    def get_available_abilities(cls) -> list[str]:
        """Get list of all registered ability names"""
        return list(cls._abilities.keys())

# Convenience function
def create_ability(name: str) -> Ability:
    """Create an ability by name"""
    return AbilityFactory.create_ability(name)