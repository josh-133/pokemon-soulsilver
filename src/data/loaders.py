import json
import os
from models.move import Move, MoveEffects, HitInfo
from models.pokemon import Pokemon
from models.base_stats import BaseStats
from models.abilities import Static
from models.types import Type

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "pokemon.json"), "r") as f:
    POKEMON_DATA = json.load(f)

with open(os.path.join(base_dir, "moves.json"), "r") as f:
    MOVES_DATA = json.load(f)

def load_move(move_data):
    effects_info = MoveEffects(
        effect_chance = move_data["effect_chance"],
        ailment = move_data["meta"]["ailment"],
        drain = move_data["meta"]["drain"],
        healing = move_data["meta"]["healing"],
        ailment_chance = move_data["meta"]["ailment_chance"],
        flinch_chance = move_data["meta"]["flinch_chance"],
        stat_chance = move_data["meta"]["stat_chance"],
        is_badly_poisoning = ["is_badly_poisoning"],
    )

    if move_data["name"].lower() == "toxic":
        effects_info.is_badly_poisoning = True
    
    hit_info = HitInfo(
        min_hits  = move_data["meta"]["min_hits"],
        max_hits  = move_data["meta"]["max_hits"],
        min_turns = move_data["meta"]["min_turns"],
        max_turns = move_data["meta"]["max_turns"],
    )

    move = Move(
        name = move_data["name"],
        accuracy = move_data["accuracy"],
        pp = move_data["pp"],
        priority = move_data["priority"],
        power = move_data["power"],
        damage_class = move_data["damage_class"],
        crit_rate = move_data["meta"]["crit_rate"],
        category = move_data["meta"]["category"],
        move_type = move_data["type"],
        hit_info = hit_info,
        effects_info = effects_info,
    )

    return move


MOVE_LOOKUP = {move["name"].lower(): load_move(move) for move in MOVES_DATA}

def get_move_lookup():
    return MOVE_LOOKUP

def load_pokemon(name: str, move_lookup, level=50):
    data = next((p for p in POKEMON_DATA if p["name"].lower() == name.lower()), None)
    if not data:
        raise ValueError(f"Pokemon '{name}' not found in pokemon.json")
    
    base_stats = BaseStats(
        hp=data["stats"]["hp"],
        attack=data["stats"]["attack"],
        defense=data["stats"]["defense"],
        sp_attack=data["stats"]["special-attack"],
        sp_defense=data["stats"]["special-defense"],
        speed=data["stats"]["speed"],
    )

    ability = Static()

    default_moves = {
        "pikachu": ["thunderbolt", "quick attack", "iron tail", "electro ball"],
        "charmander": ["ember", "scratch", "growl", "smokescreen"],
        # Add more Pokémon and their moves here
    }

    types = [Type[t.upper()] for t in data["types"]]
    move_names = default_moves.get(name.lower(), [])[:4]
    moves = [move_lookup[m.lower()] for m in move_names if m.lower() in move_lookup]

    return Pokemon(
        name=data["name"],
        ability=ability,
        base_stats=base_stats,
        types=types,
        moves=moves,
        level=level,
        iv=Pokemon.generate_random_iv(),
        ev=Pokemon.generate_default_ev(),
    )