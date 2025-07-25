import json
import os
from models.move import Move, MoveEffects, HitInfo
from models.pokemon import Pokemon, load_sprite
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
        move_type = Type[move_data["type"].upper()],
        hit_info = hit_info,
        effects_info = effects_info,
    )

    return move

MOVE_LOOKUP = {move["name"].lower(): load_move(move) for move in MOVES_DATA}

def get_move_lookup():
    return MOVE_LOOKUP


def extract_level_up_moves(pokemon_data, move_lookup, level=50, version_group="heartgold-soulsilver"):
    selected_moves = []
    
    for move_entry in pokemon_data["moves"]:
        move_name = move_entry["move"]["name"]

        for detail in move_entry["version_group_details"]:
            method = detail["move_learn_method"]["name"]
            version = detail["version_group"]["name"]
            learned_at = detail["level_learned_at"]

            is_level_up = method == "level-up"
            is_valid_version = version == version_group
            is_valid_level = learned_at <= level

            print(f"move: {move_name}")
            print(f"- version: {version}")
            print(f"- level: {learned_at}")
            print(f"-> is_level_up: {is_level_up}, is_valid_version: {is_valid_version}, is_valid_level: {is_valid_level}")

            if is_level_up and is_valid_version and is_valid_level:
                move_obj = move_lookup.get(move_name)
                if move_obj and move_obj not in selected_moves:
                    selected_moves.append(move_obj)
    
    return selected_moves[:4]

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

    sprites = data["sprites"]
    front_url = sprites.get("front_default")
    back_url = sprites.get("back_default")

    front_sprite = load_sprite(front_url)
    back_sprite = load_sprite(back_url)

    ability = Static()

    types = [Type[t.upper()] for t in data["types"]]
    moves = extract_level_up_moves(pokemon_data=data, move_lookup=move_lookup, level=50, version_group="heartgold-soulsilver")

    print(moves)

    return Pokemon(
        name=data["name"],
        ability=ability,
        base_stats=base_stats,
        types=types,
        moves=moves,
        level=level,
        iv=Pokemon.generate_random_iv(),
        ev=Pokemon.generate_default_ev(),
        front_sprite=front_sprite,
        back_sprite=back_sprite,
    )