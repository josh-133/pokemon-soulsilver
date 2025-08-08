"""Test fixtures for battle scenarios"""
import pytest
from models.player import Player
from models.battle_manager import BattleManager
from .pokemon_data import charizard, blastoise, venusaur

@pytest.fixture
def player_with_charizard(charizard):
    """Player with a single Charizard"""
    player = Player(name="Ash", is_ai=False)
    player.team = [charizard]
    player.active_index = 0
    return player

@pytest.fixture
def player_with_blastoise(blastoise):
    """Player with a single Blastoise"""
    player = Player(name="Gary", is_ai=True)
    player.team = [blastoise]
    player.active_index = 0
    return player

@pytest.fixture
def player_with_full_team(charizard, blastoise, venusaur):
    """Player with a full team of 3 Pokemon"""
    player = Player(name="Trainer", is_ai=False)
    player.team = [charizard, blastoise, venusaur]
    player.active_index = 0
    return player

@pytest.fixture
def basic_battle(player_with_charizard, player_with_blastoise):
    """Basic battle setup between Charizard and Blastoise"""
    return BattleManager(player_with_charizard, player_with_blastoise)

@pytest.fixture
def type_advantage_battle(charizard, blastoise):
    """Battle where one Pokemon has type advantage"""
    # Charizard vs Blastoise - Water beats Fire
    player1 = Player(name="Player1", is_ai=False)
    player1.team = [charizard]
    player1.active_index = 0
    
    player2 = Player(name="Player2", is_ai=True)
    player2.team = [blastoise]
    player2.active_index = 0
    
    return BattleManager(player1, player2)

@pytest.fixture
def status_effect_battle(charizard, venusaur):
    """Battle setup for testing status effects"""
    # Charizard vs Venusaur - good for testing poison/sleep
    player1 = Player(name="Player1", is_ai=False)
    player1.team = [charizard]
    player1.active_index = 0
    
    player2 = Player(name="Player2", is_ai=True)  
    player2.team = [venusaur]
    player2.active_index = 0
    
    return BattleManager(player1, player2)