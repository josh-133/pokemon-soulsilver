from fastapi import FastAPI, HTTPException
import requests
from .save_utils import save_json

# start app
app = FastAPI()

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

@app.get("/load/all_pokemon")
def load_all_pokemon():
    pokemon_list = []

    try:
        for id in range(1,494): 

            response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{id}/")
            response.raise_for_status()
            pokemon_data = response.json()

            cleaned_data = {
                "id": pokemon_data["id"],
                "name": pokemon_data["name"],
                "abilities": pokemon_data["abilities"],
                "sprites": pokemon_data["sprites"]["versions"]["generation-iv"]["heartgold-soulsilver"],
                "stats": {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in pokemon_data["stats"]
                },
                "types": [t["type"]["name"] for t in pokemon_data["types"]],

            }

            pokemon_list.append(cleaned_data)
        
        save_json("pokemon.json", pokemon_list)
        return pokemon_list
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Error fetching data")
    # except Exception:
    #     raise HTTPException(status_code=404, detail="Pokemon not found")
    
@app.get("/load/all_moves")
def load_all_moves():
    moves_list = []

    try:
        for id in range(1,468): 

            response = requests.get(f"{POKEAPI_BASE_URL}/move/{id}/")
            response.raise_for_status()
            moves_data = response.json()

            cleaned_data = {
                "id": moves_data["id"],
                "name": moves_data["name"],
                "accuracy": moves_data["accuracy"],
                "effect_chance": moves_data["effect_chance"],
                "pp": moves_data["pp"],
                "priority": moves_data["priority"],
                "power": moves_data["power"],
                "contest_combos": moves_data["contest_combos"],
                "damage_class": moves_data["damage_class"]["name"],
                "effect_entries": [effect["effect"] for effect in moves_data["effect_entries"]],
                "effect_changes": moves_data["effect_changes"],
                "meta": {
                    "ailment": moves_data["meta"]["ailment"]["name"],
                    "category": moves_data["meta"]["category"]["name"],
                    "min_hits": moves_data["meta"]["min_hits"],
                    "max_hits": moves_data["meta"]["max_hits"],
                    "min_turns": moves_data["meta"]["min_turns"],
                    "max_turns": moves_data["meta"]["max_turns"],
                    "drain": moves_data["meta"]["drain"],
                    "healing": moves_data["meta"]["healing"],
                    "crit_rate": moves_data["meta"]["crit_rate"],
                    "ailment_chance": moves_data["meta"]["ailment_chance"],
                    "flinch_chance": moves_data["meta"]["flinch_chance"],
                    "stat_chance": moves_data["meta"]["stat_chance"],
                },
                "stat_changes": moves_data["stat_changes"],
                "target": moves_data["target"]["name"],
                "type": moves_data["type"]["name"],
            }

            moves_list.append(cleaned_data)
        
        save_json("moves.json", moves_list)
        return moves_list
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Error fetching data")
    except Exception:
        raise HTTPException(status_code=404, detail="Move not found")
    
@app.get("/load/all_abilities")
def load_all_abilities():
    abilities_list = []

    try:
        for id in range(1,124): 

            response = requests.get(f"{POKEAPI_BASE_URL}/ability/{id}/")
            response.raise_for_status()
            abilities_data = response.json()

            effect_changes = []
            for change in abilities_data["effect_changes"]:
                english_entry = next(
                    (entry["effect"] for entry in change["effect_entries"] if entry["language"]["name"] == "en"),
                    None
                )
                if english_entry:
                    effect_changes.append({
                        "effect": english_entry,
                        "version_group": change["version_group"]["name"]
                    })

            cleaned_data = {
                "id": abilities_data["id"],
                "name": abilities_data["name"],
                "effect_entries": {
                    "effect": next(entry["effect"] for entry in abilities_data["effect_entries"] if entry["language"]["name"] == "en"),
                    "short_effect": next(entry["short_effect"] for entry in abilities_data["effect_entries"] if entry["language"]["name"] == "en"),
                },
                "effect_changes": effect_changes,
                "pokemon": abilities_data["pokemon"],
            }

            abilities_list.append(cleaned_data)
        
        save_json("abilities.json", abilities_list)
        return abilities_list
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Error fetching data")
    # except Exception:
    #     raise HTTPException(status_code=404, detail="Ability not found")