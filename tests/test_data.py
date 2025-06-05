from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..src.data.api_client.main import app

def test_get_pokemon_data():
    client = TestClient(app)
    response = client.get("/load/all_pokemon")
    assert response.status_code == 200

def test_get_moves_data():
    client = TestClient(app)
    response = client.get("/load/all_moves")
    assert response.status_code == 200

def test_get_abilities_data():
    client = TestClient(app)
    response = client.get("/load/all_abilities")
    assert response.status_code == 200