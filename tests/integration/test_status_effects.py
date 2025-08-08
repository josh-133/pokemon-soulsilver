"""Integration tests for status effects in battle"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.player_action import PlayerAction
from tests.fixtures.battle_scenarios import status_effect_battle
from tests.fixtures.pokemon_data import create_test_move, charizard, venusaur


class TestStatusEffectsIntegration:
    
    def test_paralysis_application_and_effects(self, status_effect_battle):
        """Test paralysis status from move application through battle effects"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        venusaur = battle.opponent.active_pokemon()
        
        # Charizard uses Thunder Punch (10% paralysis chance)
        thunder_punch = charizard.get_move_by_name("Thunder Punch")
        
        # Force paralysis for testing by temporarily modifying the move
        original_chance = thunder_punch.effects_info.ailment_chance
        thunder_punch.effects_info.ailment_chance = 100  # 100% chance
        
        # Execute move and apply effects
        damage, is_critical, missed = battle.execute_move_calculate_only(
            battle.player, battle.opponent, thunder_punch
        )
        
        if not missed and damage is not None:
            battle.apply_calculated_damage(
                battle.player, battle.opponent, thunder_punch, damage, is_critical
            )
            battle.apply_move_effects(battle.player, battle.opponent, thunder_punch)
            
            # Check if paralysis was applied
            assert venusaur.battle_stats.status == "paralysis"
            
            # Test speed reduction
            normal_speed = venusaur.stats["speed"]
            paralyzed_speed = venusaur.battle_stats.get_effective_stat("speed")
            assert paralyzed_speed == int(normal_speed * 0.25)
        
        # Restore original chance
        thunder_punch.effects_info.ailment_chance = original_chance
    
    def test_paralysis_prevents_movement(self, status_effect_battle):
        """Test that paralysis can prevent Pokemon from moving"""
        battle = status_effect_battle
        venusaur = battle.opponent.active_pokemon()
        
        # Apply paralysis directly
        venusaur.battle_stats.status = "paralysis"
        
        # Test movement prevention multiple times (25% chance)
        movement_prevented = 0
        total_tests = 100
        
        for _ in range(total_tests):
            can_move, message = battle.check_status_prevents_move(battle.opponent)
            if not can_move:
                movement_prevented += 1
                assert "paralyzed" in message.lower()
                assert "can't move" in message.lower()
        
        # Should prevent movement roughly 25% of the time
        # Allow for variance in random testing
        assert 15 <= movement_prevented <= 35
    
    def test_sleep_application_and_duration(self, status_effect_battle):
        """Test sleep status application and turn countdown"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        venusaur = battle.opponent.active_pokemon()
        
        # Venusaur uses Sleep Powder (100% sleep chance in our test data)
        sleep_powder = venusaur.get_move_by_name("Sleep Powder")
        
        # Execute move and apply effects
        battle.apply_move_effects(battle.opponent, battle.player, sleep_powder)
        
        # Check if sleep was applied
        assert charizard.battle_stats.status == "sleep"
        assert charizard.battle_stats.sleep_turns > 0
        assert 1 <= charizard.battle_stats.sleep_turns <= 3  # Should be 1-3 turns
    
    def test_sleep_prevents_movement_and_countdown(self, status_effect_battle):
        """Test sleep prevents movement and counts down turns"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        
        # Apply sleep directly
        charizard.battle_stats.status = "sleep"
        charizard.battle_stats.sleep_turns = 2
        
        # First check - should be prevented and turn count decreases
        can_move, message = battle.check_status_prevents_move(battle.player)
        assert not can_move
        assert "fast asleep" in message.lower()
        assert charizard.battle_stats.sleep_turns == 1
        
        # Second check - should be prevented and turn count becomes 0
        can_move, message = battle.check_status_prevents_move(battle.player)
        assert not can_move
        assert charizard.battle_stats.sleep_turns == 0
        
        # Third check - should wake up
        can_move, message = battle.check_status_prevents_move(battle.player)
        assert can_move
        assert "woke up" in message.lower()
        assert charizard.battle_stats.status is None
    
    def test_poison_application_and_damage(self, status_effect_battle):
        """Test poison status application and end-of-turn damage"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        venusaur = battle.opponent.active_pokemon()
        
        # Venusaur uses Poison Powder
        poison_powder = venusaur.get_move_by_name("Poison Powder")
        battle.apply_move_effects(battle.opponent, battle.player, poison_powder)
        
        # Check if poison was applied
        assert charizard.battle_stats.status == "poison"
        
        # Test end-of-turn poison damage
        initial_hp = charizard.battle_stats.current_hp
        status_effects = battle.apply_end_of_turn_status_effects([charizard])
        
        # Should return damage info for poison
        assert len(status_effects) > 0
        owner, new_hp, message = status_effects[0]
        assert "poison" in message.lower()
        assert new_hp < initial_hp  # Should take damage
        
        # Poison damage should be 1/8 of max HP
        expected_damage = max(1, charizard.battle_stats.max_hp // 8)
        assert new_hp == initial_hp - expected_damage
    
    def test_burn_application_and_damage(self, status_effect_battle):
        """Test burn status application and effects"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        
        # Apply burn directly for testing
        charizard.battle_stats.status = "burn"
        
        # Test end-of-turn burn damage
        initial_hp = charizard.battle_stats.current_hp
        status_effects = battle.apply_end_of_turn_status_effects([charizard])
        
        # Should return damage info for burn
        assert len(status_effects) > 0
        owner, new_hp, message = status_effects[0]
        assert "burn" in message.lower()
        assert new_hp < initial_hp
        
        # Burn damage should be 1/16 of max HP
        expected_damage = max(1, charizard.battle_stats.max_hp // 16)
        assert new_hp == initial_hp - expected_damage
    
    def test_burn_reduces_physical_attack(self, status_effect_battle):
        """Test that burn reduces physical attack damage"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        venusaur = battle.opponent.active_pokemon()
        
        # Get a physical move
        physical_move = None
        for move in charizard.moves:
            if move.damage_class == "Physical":
                physical_move = move
                break
        
        # If no physical move in test data, create one
        if physical_move is None:
            from tests.fixtures.pokemon_data import create_test_move
            physical_move = create_test_move("Tackle", power=40, damage_class="Physical")
            charizard.moves.append(physical_move)
            charizard.battle_stats.pp[physical_move.name] = physical_move.pp
        
        # Calculate normal damage
        normal_damage, _ = battle.calculate_damage(battle.player, battle.opponent, physical_move)
        
        # Apply burn and calculate damage again
        charizard.battle_stats.status = "burn"
        burned_damage, _ = battle.calculate_damage(battle.player, battle.opponent, physical_move)
        
        # Burned damage should be halved
        assert burned_damage <= normal_damage // 2
    
    def test_status_effect_immunity(self, status_effect_battle):
        """Test that Pokemon with status can't get another status"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        
        # Apply paralysis first
        charizard.battle_stats.status = "paralysis"
        
        # Try to apply sleep
        charizard.battle_stats.apply_status("sleep")
        
        # Should still be paralyzed
        assert charizard.battle_stats.status == "paralysis"
    
    def test_multiple_status_effects_end_of_turn(self, status_effect_battle):
        """Test handling multiple Pokemon with status effects"""
        battle = status_effect_battle
        charizard = battle.player.active_pokemon()
        venusaur = battle.opponent.active_pokemon()
        
        # Apply different status to each Pokemon
        charizard.battle_stats.status = "poison"
        venusaur.battle_stats.status = "burn"
        
        # Get end-of-turn effects for both
        status_effects = battle.apply_end_of_turn_status_effects([charizard, venusaur])
        
        # Should have effects for both Pokemon
        assert len(status_effects) >= 2  # At least 2 (could be more with damage messages)
        
        # Check that both Pokemon have status damage
        messages = [effect[2] for effect in status_effects]
        has_poison = any("poison" in msg.lower() for msg in messages)
        has_burn = any("burn" in msg.lower() for msg in messages)
        assert has_poison
        assert has_burn