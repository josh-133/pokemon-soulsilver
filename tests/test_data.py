import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from data.api_client.main import app

@pytest.mark.slow
@pytest.mark.skip(reason="Slow external API test - run manually when needed")
def test_get_pokemon_data():
    """Test fetching Pokemon data from PokeAPI (SLOW - skipped in CI)"""
    client = TestClient(app)
    response = client.get("/load/all_pokemon")
    assert response.status_code == 200

@pytest.mark.slow
@pytest.mark.skip(reason="Slow external API test - run manually when needed")
def test_get_moves_data():
    """Test fetching moves data from PokeAPI (SLOW - skipped in CI)"""
    client = TestClient(app)
    response = client.get("/load/all_moves")
    assert response.status_code == 200

@pytest.mark.slow  
@pytest.mark.skip(reason="Slow external API test - run manually when needed")
def test_get_abilities_data():
    """Test fetching abilities data from PokeAPI (SLOW - skipped in CI)"""
    client = TestClient(app)
    response = client.get("/load/all_abilities")
    assert response.status_code == 200