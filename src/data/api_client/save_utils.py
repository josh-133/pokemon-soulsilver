import json
import os

def save_json(filename: str, data: list):
    path = os.path.join("data", filename)
    with open(path, "a") as f:
        json.dump(data, f, indent=4)
        f.write(",\n")