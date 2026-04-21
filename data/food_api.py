import requests
import json
import os
import random

BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"
CACHE_FILE = "data/cache.json"
FALLBACK_FILE = "data/foods_fallback.json"

# liste recherche ed base
CANDIDATES = {
    "proteine": ["poulet", "thon", "saumon", "oeuf", "tofu", "crevettes"],
    "glucide":  ["riz", "pates completes", "patate douce", "quinoa", "lentilles"],
    "legume":   ["brocoli", "epinards", "haricots verts", "courgette", "tomate"],
}

# User-Agent pour pas que les requêtes API soient bloquées
HEADERS = {"User-Agent": "NutriBot/1.0 (Discord nutrition bot)"}


def load_cache():
    # Charge cache recherches API précé
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
# Enregistre cache pour éviter requêtes API similères
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def load_fallback(category):
# Charge la DB locale d'aliments pour une caté
    try:
        with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get(category, [])
    except Exception:
        return []



def search_food_off(query, category):
# Cherche un aliment sur l'API et gestion du cache local
# Vérif le cache pour éviter des appels API inutiles
    cache = load_cache()
    if query in cache:
        return cache[query]

    params = {
        "search_terms": query, "json": 1, "page_size": 8,
        "sort_by": "unique_scans_n",
        "fields": "product_name,nutriments,nutrition_grades",
    }

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=6)
        resp.raise_for_status()
        products = resp.json().get("products", [])
    except Exception as e:
        print(f"[OFF API] Erreur pour '{query}' : {e}")
        return []

# Extrait mots clés significatifs de la requête (> 2 caractères)
    query_words = [w for w in query.lower().split() if len(w) > 2]
    results = []

    for p in products:
        n = p.get("nutriments", {})
        name = p.get("product_name", "").strip()
        cal = n.get("energy-kcal_100g", 0) or 0
        prot = n.get("proteins_100g", 0) or 0
        carbs = n.get("carbohydrates_100g", 0) or 0

# Rejette aliments sans données ou avec calories bizzares
        if not name or cal <= 0 or cal > 900:
            continue

# S'assure que le mot-clé est dans les 25 premiers caractères (ingrédient principal)
        if not any(w in name.lower()[:25] for w in query_words):
            continue

        if category == "proteine" and prot < 10:
            continue
        if category == "glucide" and carbs < 20:
            continue
        if category == "legume" and (cal > 150 or prot > 15):
            continue

        results.append({
            "name": name,
            "calories": round(cal, 1),
            "proteins": round(prot, 1),
            "carbs": round(carbs, 1),
            "fats": round(n.get("fat_100g", 0) or 0, 1),
            "source": "OpenFoodFacts",
        })

# Enregistre résultats en cache pour accél les futures recherches
    if results:
        cache[query] = results
        save_cache(cache)

    return results

def search_food_by_name(food_name, category="proteine"):
# Cherche un aliment spécifique
    name_lower = food_name.lower()

    for food in search_food_off(food_name, category):
        if name_lower in food["name"].lower()[:30]:
            return food
#__
    for food in load_fallback(category):
        if name_lower in food["name"].lower():
            return food

    return None


# cherche random/caté

def is_excluded(food_name, excluded):
# Vérifie si aliment est pas dans la liste exclu user
    for ex in excluded:
        if ex.lower() in food_name.lower():
            return True
    return False


def get_food_for_category(category, excluded=[]):
# Sélect random un aliment pour une caté, en excluant les aliments interdits.
# Essaie OpenFoodFacts d'abord, puis la base locale en dernier recours.
    candidates = list(CANDIDATES.get(category, []))
    random.shuffle(candidates)

# Essaie chaque aliment possibles sur OpenFoodFacts
    for query in candidates:
        if query in excluded:
            continue

        results = search_food_off(query, category)
        for food in results:
            if not is_excluded(food["name"], excluded):
                food["qty"] = 150 if category == "proteine" else 100
                return food

#Utilise la base locale si OpenFoodFacts n'a rien trouvé
    fallback = load_fallback(category)
    available = [f for f in fallback if not is_excluded(f["name"], excluded)]
    if available:
        food = random.choice(available)
        food["source"] = "local"
        food["qty"] = 150 if category == "proteine" else 100
        return food

    return None
