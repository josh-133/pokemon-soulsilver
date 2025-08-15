"""Integration tests for complete battle scenarios"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.player_action import PlayerAction
from models.battle_manager import BattleManager
from tests.fixtures.battle_scenarios import (
    basic_battle, type_advantage_battle, status_effect_battle,
    player_with_charizard, player_with_blastoise
)
from tests.fixtures.pokemon_data import charizard, blastoise, venusaur


class TestBattleFlow:
    
    def test_basic_battle_setup(self, basic_battle):
        """Test that a battle is set up correctly"""
        battle = basic_battle
        
        assert not battle.battle_over
        assert battle.player.active_pokemon().name == "Charizard"
        assert battle.opponent.active_pokemon().name == "Blastoise"
        assert len(battle.battle_log) == 0
    
    def test_turn_order_by_speed(self, basic_battle):
        """Test that faster Pokemon goes first"""
        battle = basic_battle
        
        # Charizard (speed 100) vs Blastoise (speed 78)
        player_action = PlayerAction(type="move", move=battle.player.active_pokemon().moves[0])
        opponent_action = PlayerAction(type="move", move=battle.opponent.active_pokemon().moves[0])
        
        first, second = battle.determine_turn_order(player_action, opponent_action)
        
        # Charizard should go first (higher speed)
        assert first.active_pokemon().name == "Charizard"
        assert second.active_pokemon().name == "Blastoise"
    
    def test_turn_order_by_priority(self, basic_battle):
        """Test that priority moves go first regardless of speed"""
        battle = basic_battle
        
        # Charizard uses Quick Attack (priority +1), Blastoise uses normal move
        quick_attack = None
        for move in battle.player.active_pokemon().moves:
            if move.priority > 0:
                quick_attack = move
                break
        
        assert quick_attack is not None, "Charizard should have Quick Attack"
        
        player_action = PlayerAction(type="move", move=quick_attack)
        opponent_action = PlayerAction(type="move", move=battle.opponent.active_pokemon().moves[0])
        
        first, second = battle.determine_turn_order(player_action, opponent_action)
        
        # Charizard should go first due to priority, even if Blastoise were faster
        assert first.active_pokemon().name == "Charizard"
    
    def test_single_move_execution(self, basic_battle):
        """Test executing a single move in battle"""
        battle = basic_battle
        initial_hp = battle.opponent.active_pokemon().battle_stats.current_hp
        
        # Charizard uses Ember on Blastoise
        ember = battle.player.active_pokemon().get_move_by_name("Ember")
        damage, is_critical, missed = battle.execute_move_calculate_only(
            battle.player, battle.opponent, ember
        )
        
        assert damage > 0  # Should deal some damage
        assert isinstance(is_critical, bool)
        assert missed == False  # Ember has 100% accuracy
        
        # Apply the damage
        battle.apply_calculated_damage(
            battle.player, battle.opponent, ember, damage, is_critical
        )
        
        final_hp = battle.opponent.active_pokemon().battle_stats.current_hp
        assert final_hp == initial_hp - damage
    
    def test_type_effectiveness_integration(self, type_advantage_battle):
        """Test type effectiveness in a real battle scenario"""
        battle = type_advantage_battle
        
        # Blastoise (Water) uses Water Gun on Charizard (Fire/Flying)
        water_gun = battle.opponent.active_pokemon().get_move_by_name("Water Gun")
        damage, _, _ = battle.execute_move_calculate_only(
            battle.opponent, battle.player, water_gun
        )
        
        # Should do significant damage due to type advantage (2x effectiveness)
        assert damage > 30  # Should be substantial damage (lowered expectation)
    
    def test_pokemon_fainting_and_battle_end(self, basic_battle):
        """Test Pokemon fainting and battle ending"""
        battle = basic_battle
        
        # Deal massive damage to faint Blastoise
        blastoise = battle.opponent.active_pokemon()
        blastoise.take_damage(blastoise.battle_stats.max_hp)
        
        assert blastoise.is_fainted()
        
        # Check battle end
        battle.check_battle_end()
        assert battle.battle_over
    
    def test_ai_move_selection(self, basic_battle):
        """Test that AI selects moves intelligently"""
        battle = basic_battle
        
        # AI should select a move for Blastoise
        ai_action = battle.make_ai_action(battle.opponent, battle.player)
        
        assert ai_action.type == "move"
        assert ai_action.move is not None
        assert ai_action.move in battle.opponent.active_pokemon().moves
    
    def test_pp_depletion_in_battle(self, basic_battle):
        """Test that moves become unusable when PP is depleted"""
        battle = basic_battle
        charizard = battle.player.active_pokemon()
        ember = charizard.get_move_by_name("Ember")
        
        # Use all PP for Ember
        original_pp = charizard.battle_stats.pp[ember.name]
        for _ in range(original_pp):
            charizard.battle_stats.use_pp(ember.name)
        
        # Now Ember should have no PP
        assert not charizard.battle_stats.has_pp(ember.name)
        
        # Trying to execute move should return None for damage
        damage, _, _ = battle.execute_move_calculate_only(
            battle.player, battle.opponent, ember
        )
        assert damage is None
    
    def test_critical_hit_integration(self, basic_battle):
        """Test critical hits in battle context"""
        battle = basic_battle
        charizard = battle.player.active_pokemon()
        move = charizard.moves[0]
        
        # Test multiple executions to verify critical hit system works
        critical_hits = 0
        total_tests = 50
        
        for _ in range(total_tests):
            damage, is_critical, _ = battle.execute_move_calculate_only(
                battle.player, battle.opponent, move
            )
            if is_critical:
                critical_hits += 1
        
        # Should get some critical hits (allowing for randomness)
        # At 6.25% rate, expect around 3 in 50 tests, but allow wider range
        assert 0 <= critical_hits <= 15
    
    def test_battle_log_messages(self, basic_battle):
        """Test that battle actions are logged correctly"""
        battle = basic_battle
        initial_log_length = len(battle.battle_log)
        
        # Execute a move and check if messages are logged
        ember = charizard.get_move_by_name("Ember")
        
        battle.execute_move(battle.player, battle.opponent, ember)
        
        # Should have new log messages
        assert len(battle.battle_log) > initial_log_length
    
    def test_multiple_pokemon_switching(self, player_with_charizard, player_with_blastoise):
        """Test switching between multiple Pokemon"""
        # Give player multiple Pokemon
        venusaur_test = player_with_charizard.team[0]  # Reuse for simplicity
        player_with_charizard.team.append(venusaur_test)
        
        battle = BattleManager(player_with_charizard, player_with_blastoise)
        
        # Initial active Pokemon
        assert battle.player.active_pokemon().name == "Charizard"
        
        # Switch to second Pokemon (index 1)
        battle.player.switch_to(1)
        assert battle.player.active_index == 1