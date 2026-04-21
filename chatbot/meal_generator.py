#Génération de repas complets

from data.food_api import get_food_for_category
from chatbot.nutrition import calculate_meal_macros

# Configuration pour chaque objectif  label, couleur, emoji et conseil perso
OBJECTIVES_CONFIG = {
    "masse":    {"label": "Prise de masse 💪", "color": 0xE67E22, "emoji": "🟠",
                 "tip": "Mange tes glucides 30 min avant et après la séance !"},
    "seche":    {"label": "Sèche 🔥", "color": 0xE74C3C, "emoji": "🔴",
                 "tip": "Bois au moins 2L d'eau aujourd'hui."},
    "maintien": {"label": "Maintien ⚖️", "color": 0x2ECC71, "emoji": "🟢",
                 "tip": "Régularité > intensité pour le maintien."},
}

def generate_meal(objective, excluded=[], tdee=2000):
# Génère repas complet avec les  3 catégories
# Exclut aliments user ne veut pas et adapte les kcal à son objectif.
    foods = {}
    for cat in ["proteine", "glucide", "legume"]:
        food = get_food_for_category(cat, excluded)
        if food:
            foods[cat] = food

    return {
        "foods": foods,
        "macros": calculate_meal_macros(list(foods.values())),
        "config": OBJECTIVES_CONFIG.get(objective, OBJECTIVES_CONFIG["maintien"]),
        "tdee": tdee,
        "meal_target": tdee // 3,
    }

# smileys, 💪🟠🔥🔴⚖️🟢