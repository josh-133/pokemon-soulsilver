"""Unit tests for BattleStats class"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.battle_stats import BattleStats
from tests.fixtures.pokemon_data import create_test_pokemon, charizard


class TestBattleStats:
    
    def test_battle_stats_initialization(self, charizard):
        """Test BattleStats initialization"""
        stats = charizard.battle_stats
        
        assert stats.current_hp == stats.max_hp
        assert stats.status is None
        assert stats.badly_poisoned == False
        assert stats.toxic_turns == 0
        assert stats.sleep_turns == 0
        assert len(stats.pp) == len(charizard.moves)
    
    def test_status_application(self, charizard):
        """Test applying status conditions"""
        stats = charizard.battle_stats
        
        # Test applying paralysis
        stats.apply_status("paralysis")
        assert stats.status == "paralysis"
        
        # Test that status can't be overwritten
        stats.apply_status("poison")
        assert stats.status == "paralysis"  # Should remain paralyzed
    
    def test_stat_modifications(self, charizard):
        """Test stat stage modifications"""
        stats = charizard.battle_stats
        
        # Test increasing attack
        original_attack = stats.get_effective_stat("attack")
        stats.modify_stat("attack", 2)  # +2 stages
        boosted_attack = stats.get_effective_stat("attack")
        
        assert boosted_attack > original_attack
        assert stats.stat_modifiers["attack"] == 2
    
    def test_stat_modification_caps(self, charizard):
        """Test that stat modifications are capped at -6/+6"""
        stats = charizard.battle_stats
        
        # Test upper cap
        stats.modify_stat("attack", 10)  # Try to boost by 10 stages
        assert stats.stat_modifiers["attack"] == 6  # Should be capped at 6
        
        # Test lower cap
        stats.modify_stat("attack", -20)  # Try to lower by 20 stages
        assert stats.stat_modifiers["attack"] == -6  # Should be capped at -6
    
    def test_effective_stat_calculation(self, charizard):
        """Test effective stat calculation with modifiers"""
        stats = charizard.battle_stats
        base_attack = stats.get_effective_stat("attack")
        
        # +1 stage should multiply by 1.5
        stats.modify_stat("attack", 1)
        boosted_attack = stats.get_effective_stat("attack")
        expected_boosted = int(base_attack * 1.5)
        assert boosted_attack == expected_boosted
        
        # Reset and test -1 stage (multiply by 2/3)
        stats.stat_modifiers["attack"] = -1
        lowered_attack = stats.get_effective_stat("attack")
        expected_lowered = int(base_attack * (2/3))
        assert lowered_attack == expected_lowered
    
    def test_paralysis_speed_reduction(self, charizard):
        """Test that paralysis reduces speed to 25%"""
        stats = charizard.battle_stats
        normal_speed = stats.get_effective_stat("speed")
        
        # Apply paralysis
        stats.status = "paralysis"
        paralyzed_speed = stats.get_effective_stat("speed")
        
        # Should be 25% of normal speed
        expected_speed = int(normal_speed * 0.25)
        assert paralyzed_speed == expected_speed
    
    def test_hp_management(self, charizard):
        """Test HP damage and healing"""
        stats = charizard.battle_stats
        max_hp = stats.max_hp
        
        # Take damage
        stats.take_damage(50)
        assert stats.current_hp == max_hp - 50
        
        # Heal some
        stats.heal(20)
        assert stats.current_hp == max_hp - 30
        
        # Overheal protection
        stats.heal(1000)
        assert stats.current_hp == max_hp
    
    def test_pp_management(self, charizard):
        """Test PP usage and tracking"""
        stats = charizard.battle_stats
        move = charizard.moves[0]
        original_pp = stats.pp[move.name]
        
        # Use PP
        assert stats.has_pp(move.name)
        stats.use_pp(move.name)
        assert stats.pp[move.name] == original_pp - 1
        
        # Deplete all PP
        for _ in range(stats.pp[move.name]):
            stats.use_pp(move.name)
        
        assert stats.pp[move.name] == 0
        assert not stats.has_pp(move.name)
        
        # Test error when using PP on depleted move
        with pytest.raises(ValueError):
            stats.use_pp(move.name)
    
    def test_faint_status(self, charizard):
        """Test faint detection"""
        stats = charizard.battle_stats
        
        # Not fainted initially
        assert not stats.is_fainted()
        
        # Faint the Pokemon
        stats.take_damage(stats.max_hp)
        assert stats.is_fainted()
        assert stats.current_hp == 0
    
    def test_accuracy_evasion_multipliers(self, charizard):
        """Test accuracy and evasion stage multipliers"""
        stats = charizard.battle_stats
        
        # Test accuracy boost (+1 stage = 4/3 multiplier)
        acc_multiplier = stats.get_acc_eva_multiplier(1)
        assert acc_multiplier == 4/3
        
        # Test accuracy drop (-1 stage = 3/4 multiplier)
        acc_multiplier = stats.get_acc_eva_multiplier(-1)
        assert acc_multiplier == 3/4
        
        # Test evasion boost (+2 stage = 5/3 multiplier)
        eva_multiplier = stats.get_acc_eva_multiplier(2)
        assert eva_multiplier == 5/3
    
    def test_sleep_turns_tracking(self, charizard):
        """Test sleep turn countdown"""
        stats = charizard.battle_stats
        
        # Apply sleep
        stats.status = "sleep"
        stats.sleep_turns = 3
        
        # Should be asleep
        assert stats.status == "sleep"
        assert stats.sleep_turns == 3
        
        # Sleep turns should countdown
        stats.sleep_turns -= 1
        assert stats.sleep_turns == 2
        
        # When sleep_turns reaches 0, Pokemon should wake up
        stats.sleep_turns = 0
        stats.status = None  # Simulate waking up
        assert stats.status is None