import json
import os

STORAGE_FILE = "storage/users.json"

# Profil initial
DEFAULTS = {
    "weight": 70, "height": 175, "age": 25,
    "gender": "homme", "activity": "modéré",
    "objective": None, "excluded": [], "history": [],
    "setup_done": False,
}


def get_profile(user_id):
    # Récupère le profil user
    # Si infos manquantes met valeurs par défaut.
    profiles = {}
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except (json.JSONDecodeError, ValueError):
            profiles = {}

    profile = profiles.get(str(user_id), {})

    for key, value in DEFAULTS.items():
        if key not in profile:
            profile[key] = value

    return profile


def save_profile(user_id, profile):
    # save profil dans Json
    os.makedirs("storage", exist_ok=True)

    profiles = {}
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except (json.JSONDecodeError, ValueError):
            profiles = {}

    profiles[str(user_id)] = profile
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

def add_meal_to_history(user_id, meal):
    profile = get_profile(user_id)

# Construit une entrée simplifiée
    entry = {
        "foods": {cat: food.get("name", "") for cat, food in meal.get("foods", {}).items()},
        "macros": meal.get("macros", {}),
        "objective": profile.get("objective", "maintien"),
    }

    profile["history"].append(entry)
    profile["history"] = profile["history"][-10:]  #garde que les 10 derniers repas
    save_profile(user_id, profile)
