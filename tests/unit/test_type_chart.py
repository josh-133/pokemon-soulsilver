"""Unit tests for type effectiveness system"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.type_chart import get_type_multiplier
from models.types import Type


class TestTypeChart:
    
    def test_super_effective_combinations(self):
        """Test super effective type combinations (2x damage)"""
        # Water vs Fire
        assert get_type_multiplier(Type.WATER, Type.FIRE) == 2.0
        
        # Fire vs Grass
        assert get_type_multiplier(Type.FIRE, Type.GRASS) == 2.0
        
        # Grass vs Water
        assert get_type_multiplier(Type.GRASS, Type.WATER) == 2.0
        
        # Electric vs Water
        assert get_type_multiplier(Type.ELECTRIC, Type.WATER) == 2.0
        
        # Electric vs Flying
        assert get_type_multiplier(Type.ELECTRIC, Type.FLYING) == 2.0
    
    def test_not_very_effective_combinations(self):
        """Test not very effective type combinations (0.5x damage)"""
        # Fire vs Water
        assert get_type_multiplier(Type.FIRE, Type.WATER) == 0.5
        
        # Water vs Grass
        assert get_type_multiplier(Type.WATER, Type.GRASS) == 0.5
        
        # Grass vs Fire
        assert get_type_multiplier(Type.GRASS, Type.FIRE) == 0.5
        
        # Electric vs Grass
        assert get_type_multiplier(Type.ELECTRIC, Type.GRASS) == 0.5
    
    def test_no_effect_combinations(self):
        """Test no effect type combinations (0x damage)"""
        # Electric vs Ground
        assert get_type_multiplier(Type.ELECTRIC, Type.GROUND) == 0.0
        
        # Normal vs Ghost
        assert get_type_multiplier(Type.NORMAL, Type.GHOST) == 0.0
        
        # Fighting vs Ghost
        assert get_type_multiplier(Type.FIGHTING, Type.GHOST) == 0.0
        
        # Ground vs Flying
        assert get_type_multiplier(Type.GROUND, Type.FLYING) == 0.0
    
    def test_normal_effectiveness(self):
        """Test normal effectiveness combinations (1x damage)"""
        # Normal vs Normal
        assert get_type_multiplier(Type.NORMAL, Type.NORMAL) == 1.0
        
        # Fire vs Electric
        assert get_type_multiplier(Type.FIRE, Type.ELECTRIC) == 1.0
        
        # Water vs Psychic
        assert get_type_multiplier(Type.WATER, Type.PSYCHIC) == 1.0
        
        # Dark vs Normal
        assert get_type_multiplier(Type.DARK, Type.NORMAL) == 1.0
    
    def test_dual_type_effectiveness(self):
        """Test type effectiveness against dual-type Pokemon"""
        # This would be tested in integration tests when calculating total damage
        # But we can test the individual components
        
        # Fire move vs Fire/Flying (Charizard)
        # Fire vs Fire = 0.5x, Fire vs Flying = 1.0x
        # Total would be 0.5x * 1.0x = 0.5x
        fire_vs_fire = get_type_multiplier(Type.FIRE, Type.FIRE)
        fire_vs_flying = get_type_multiplier(Type.FIRE, Type.FLYING)
        total_multiplier = fire_vs_fire * fire_vs_flying
        assert total_multiplier == 0.5
        
        # Electric move vs Water/Flying
        # Electric vs Water = 2.0x, Electric vs Flying = 2.0x  
        # Total would be 2.0x * 2.0x = 4.0x
        electric_vs_water = get_type_multiplier(Type.ELECTRIC, Type.WATER)
        electric_vs_flying = get_type_multiplier(Type.ELECTRIC, Type.FLYING)
        total_multiplier = electric_vs_water * electric_vs_flying
        assert total_multiplier == 4.0
    
    def test_psychic_type_interactions(self):
        """Test Psychic type effectiveness"""
        # Psychic vs Fighting (super effective)
        assert get_type_multiplier(Type.PSYCHIC, Type.FIGHTING) == 2.0
        
        # Psychic vs Poison (super effective)
        assert get_type_multiplier(Type.PSYCHIC, Type.POISON) == 2.0
        
        # Psychic vs Dark (no effect)
        assert get_type_multiplier(Type.PSYCHIC, Type.DARK) == 0.0
        
        # Psychic vs Steel (not very effective)
        assert get_type_multiplier(Type.PSYCHIC, Type.STEEL) == 0.5
    
    def test_dark_type_interactions(self):
        """Test Dark type effectiveness"""
        # Dark vs Psychic (super effective)
        assert get_type_multiplier(Type.DARK, Type.PSYCHIC) == 2.0
        
        # Dark vs Ghost (super effective)  
        assert get_type_multiplier(Type.DARK, Type.GHOST) == 2.0
        
        # Dark vs Fighting (not very effective)
        assert get_type_multiplier(Type.DARK, Type.FIGHTING) == 0.5
        
        # Dark vs Dark (not very effective)
        assert get_type_multiplier(Type.DARK, Type.DARK) == 0.5
    
    def test_steel_type_interactions(self):
        """Test Steel type effectiveness"""
        # Steel vs Rock (super effective)
        assert get_type_multiplier(Type.STEEL, Type.ROCK) == 2.0
        
        # Steel vs Ice (super effective)
        assert get_type_multiplier(Type.STEEL, Type.ICE) == 2.0
        
        # Steel vs Steel (not very effective)
        assert get_type_multiplier(Type.STEEL, Type.STEEL) == 0.5
        
        # Steel vs Fire (not very effective)
        assert get_type_multiplier(Type.STEEL, Type.FIRE) == 0.5
        
        # Steel vs Water (not very effective)
        assert get_type_multiplier(Type.STEEL, Type.WATER) == 0.5
        
        # Steel vs Electric (not very effective)
        assert get_type_multiplier(Type.STEEL, Type.ELECTRIC) == 0.5
    
    def test_all_types_exist(self):
        """Test that all Pokemon types are defined"""
        expected_types = [
            Type.NORMAL, Type.FIRE, Type.WATER, Type.ELECTRIC, Type.GRASS,
            Type.ICE, Type.FIGHTING, Type.POISON, Type.GROUND, Type.FLYING,
            Type.PSYCHIC, Type.BUG, Type.ROCK, Type.GHOST, Type.DRAGON,
            Type.DARK, Type.STEEL
        ]
        
        # Test that all types can be used in type chart
        for attack_type in expected_types:
            for defend_type in expected_types:
                multiplier = get_type_multiplier(attack_type, defend_type)
                assert isinstance(multiplier, (int, float))
                assert multiplier >= 0.0