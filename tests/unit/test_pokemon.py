"""Unit tests for Pokemon class"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.pokemon import Pokemon
from models.types import Type
from tests.fixtures.pokemon_data import create_test_pokemon, charizard, blastoise


class TestPokemon:
    
    def test_pokemon_creation(self, charizard):
        """Test basic Pokemon creation"""
        assert charizard.name == "Charizard"
        assert charizard.level == 50
        assert Type.FIRE in charizard.types
        assert Type.FLYING in charizard.types
        assert len(charizard.moves) == 4
    
    def test_pokemon_stats_calculation(self, charizard):
        """Test that Pokemon stats are calculated correctly"""
        # At level 50 with base stats, should have reasonable values
        assert charizard.stats["hp"] > 100  # Should be around 153
        assert charizard.stats["attack"] > 80
        assert charizard.stats["speed"] > 90
    
    def test_pokemon_battle_stats_initialization(self, charizard):
        """Test that battle stats are properly initialized"""
        battle_stats = charizard.battle_stats
        assert battle_stats.current_hp == battle_stats.max_hp
        assert battle_stats.status is None
        assert len(battle_stats.pp) == len(charizard.moves)
        
        # Check PP is set correctly for moves
        for move in charizard.moves:
            assert battle_stats.pp[move.name] == move.pp
    
    def test_pokemon_take_damage(self, charizard):
        """Test Pokemon taking damage"""
        original_hp = charizard.battle_stats.current_hp
        damage = 50
        
        charizard.take_damage(damage)
        
        assert charizard.battle_stats.current_hp == original_hp - damage
        assert not charizard.is_fainted()
    
    def test_pokemon_fainting(self, charizard):
        """Test Pokemon fainting when HP reaches 0"""
        charizard.take_damage(charizard.battle_stats.max_hp)
        
        assert charizard.battle_stats.current_hp == 0
        assert charizard.is_fainted()
    
    def test_pokemon_healing(self, charizard):
        """Test Pokemon healing"""
        # Damage first
        charizard.take_damage(50)
        damaged_hp = charizard.battle_stats.current_hp
        
        # Then heal
        charizard.battle_stats.heal(30)
        
        assert charizard.battle_stats.current_hp == damaged_hp + 30
    
    def test_pokemon_overheal_protection(self, charizard):
        """Test that healing doesn't exceed max HP"""
        max_hp = charizard.battle_stats.max_hp
        charizard.battle_stats.heal(1000)  # Massive overheal
        
        assert charizard.battle_stats.current_hp == max_hp
    
    def test_move_pp_usage(self, charizard):
        """Test using move PP"""
        move = charizard.moves[0]
        original_pp = charizard.battle_stats.pp[move.name]
        
        charizard.battle_stats.use_pp(move.name)
        
        assert charizard.battle_stats.pp[move.name] == original_pp - 1
        assert charizard.battle_stats.has_pp(move.name)
    
    def test_move_pp_depletion(self, charizard):
        """Test move becomes unusable when PP reaches 0"""
        move = charizard.moves[0]
        
        # Use all PP
        for _ in range(charizard.battle_stats.pp[move.name]):
            charizard.battle_stats.use_pp(move.name)
        
        assert charizard.battle_stats.pp[move.name] == 0
        assert not charizard.battle_stats.has_pp(move.name)
    
    def test_get_move_by_name(self, charizard):
        """Test finding moves by name"""
        ember = charizard.get_move_by_name("Ember")
        assert ember is not None
        assert ember.name == "Ember"
        
        # Test non-existent move
        nonexistent = charizard.get_move_by_name("Nonexistent Move")
        assert nonexistent is None