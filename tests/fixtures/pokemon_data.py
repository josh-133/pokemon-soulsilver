"""Test fixtures for Pokemon data"""
import pytest
from models.pokemon import Pokemon
from models.base_stats import BaseStats
from models.move import Move, MoveEffects, HitInfo
from models.types import Type
from models.abilities.static import Static

def create_test_pokemon(name="TestMon", level=50, hp=100, attack=50, defense=50, 
                       sp_attack=50, sp_defense=50, speed=50, types=None, moves=None):
    """Create a test Pokemon with customizable stats"""
    if types is None:
        types = [Type.NORMAL]
    if moves is None:
        moves = [create_test_move()]
    
    base_stats = BaseStats(
        hp=hp, attack=attack, defense=defense,
        sp_attack=sp_attack, sp_defense=sp_defense, speed=speed
    )
    
    return Pokemon(
        name=name,
        ability=Static(),
        base_stats=base_stats,
        types=types,
        moves=moves,
        level=level,
        iv=Pokemon.generate_default_iv(),
        ev=Pokemon.generate_default_ev(),
        front_sprite=None,
        back_sprite=None
    )

def create_test_move(name="TestMove", power=40, move_type=Type.NORMAL, 
                    accuracy=100, pp=35, priority=0, damage_class="Physical",
                    ailment="none", ailment_chance=0):
    """Create a test move with customizable properties"""
    effects = MoveEffects(
        effect_chance=ailment_chance,
        ailment=ailment,
        drain=0,
        healing=0,
        ailment_chance=ailment_chance,
        flinch_chance=0,
        stat_chance=0,
        stat_changes={},
        is_badly_poisoning=False
    )
    
    hit_info = HitInfo(min_hits=1, max_hits=1, min_turns=0, max_turns=0)
    
    return Move(
        name=name,
        accuracy=accuracy,
        pp=pp,
        priority=priority,
        power=power,
        damage_class=damage_class,
        crit_rate=0,
        target="opponent",
        category="damage",
        move_type=move_type,
        hit_info=hit_info,
        effects_info=effects
    )

@pytest.fixture
def charizard():
    """Fire/Flying type Pokemon with high attack"""
    return create_test_pokemon(
        name="Charizard",
        hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100,
        types=[Type.FIRE, Type.FLYING],
        moves=[
            create_test_move("Ember", 40, Type.FIRE, damage_class="Special"),
            create_test_move("Wing Attack", 60, Type.FLYING),
            create_test_move("Quick Attack", 40, Type.NORMAL, priority=1),
            create_test_move("Thunder Punch", 75, Type.ELECTRIC, ailment="paralysis", ailment_chance=10)
        ]
    )

@pytest.fixture
def blastoise():
    """Water type Pokemon with high defense"""
    return create_test_pokemon(
        name="Blastoise",
        hp=79, attack=83, defense=100, sp_attack=85, sp_defense=105, speed=78,
        types=[Type.WATER],
        moves=[
            create_test_move("Water Gun", 40, Type.WATER, damage_class="Special"),
            create_test_move("Bite", 60, Type.DARK),
            create_test_move("Ice Beam", 90, Type.ICE, damage_class="Special"),
            create_test_move("Body Slam", 85, Type.NORMAL, ailment="paralysis", ailment_chance=30)
        ]
    )

@pytest.fixture
def venusaur():
    """Grass/Poison type Pokemon"""
    return create_test_pokemon(
        name="Venusaur",
        hp=80, attack=82, defense=83, sp_attack=100, sp_defense=100, speed=80,
        types=[Type.GRASS, Type.POISON],
        moves=[
            create_test_move("Vine Whip", 45, Type.GRASS, damage_class="Physical"),
            create_test_move("Poison Powder", 0, Type.POISON, damage_class="Status", ailment="poison", ailment_chance=100),
            create_test_move("Sleep Powder", 0, Type.GRASS, damage_class="Status", ailment="sleep", ailment_chance=100),
            create_test_move("Sludge Bomb", 90, Type.POISON, damage_class="Special", ailment="poison", ailment_chance=30)
        ]
    )