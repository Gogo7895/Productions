import re
import random

#Motsclés pour chaque intention

KEYWORDS = {
    "masse": ["masse", "prise de masse", "grossir", "bulk", "prendre du muscle", "prendre de la masse", "se muscler"],
    "seche": ["seche", "sèche", "sécher", "secher", "perdre du poids", "maigrir", "perdre du gras", "mincir"],
    "maintien": ["maintien", "maintenir", "rester stable", "manger équilibré", "manger equilibre", "garder ma forme"],


    "repas": ["donne moi un repas", "génère un repas", "genere un repas", "j'ai faim", "j ai faim", "faim",
              "quoi manger", "je veux manger", "propose un repas", "un repas", "je veux un repas"],
    "seance": ["programme sport", "entraînement", "entrainement", "séance sport", "seance sport", "exercices",
               "je veux m'entraîner", "je veux m entrainer"],
    "tdee": ["objectif calorique", "besoins caloriques", "calories par jour", "combien de calories",
             "mon tdee", "calories journalières", "kcal par jour", "combien je dois manger"],
    "profil": ["mon profil", "voir mon profil", "mes infos", "mes paramètres", "qui suis-je"],
    "recap": ["recap", "résumé", "resume", "bilan", "historique", "mes repas", "mes stats"],


    "greeting": ["bonjour", "salut", "hello", "coucou", "hey", "yo", "bonsoir", "hi", "slt", "bjr", "cc", "wesh"],
    "thanks": ["merci", "super", "parfait", "nickel", "cool", "top", "génial", "genial"],
    "help": ["aide", "help", "comment ça marche", "tes commandes"],
}

#Regex pour les exclusions

EXCLUSION_PATTERNS = [
    r"je n'?aime pas (?:le |la |les |du |de la |des |l')?(.+)",
    r"je déteste (?:le |la |les |du |de la |des |l')?(.+)",
    r"pas de (.+)",
    r"sans (.+)",
    r"je ne mange pas de (.+)",
]

#Réponses prédéf

RESPONSES = {
    "greeting": [
        "Salut ! Je suis NutriBot, ton assistant nutrition.\nDis-moi ton objectif : **masse**, **sèche** ou **maintien** ?\n\n⚠️ *Consulte un professionnel de santé pour tout suivi personnalisé.*",
        "Hey ! Quel est ton objectif fitness du moment ?\n\n⚠️ *Suggestions indicatives uniquement.*",
    ],
    "thanks": [
        "Avec plaisir ! Tu veux un autre repas ou modifier ton profil ?\n\n⚠️ *Ces informations ne remplacent pas un avis médical.*",
    ],
    "help": [
        "Voici ce que je sais faire :\n"
        "• Dis-moi simplement ce que tu veux (ex: *\"un repas avec du poulet\"*)\n"
        "• `!repas` / `!seance` / `!profil` / `!recap`\n"
        "• `!setpoids` / `!setage` / `!setobjectif`\n"
        "• `!setup` — reconfigurer ton profil\n"
        "• `!reset` — tout réinitialiser\n\n"
        "⚠️ *NutriBot est un outil indicatif.*",
    ],
    "unknown": [
        "Je n'ai pas bien compris. Dis-moi ton objectif (**masse**, **sèche**, **maintien**) ou tape `!aide`.",
        "Essaie : *\"je veux un repas avec du saumon\"* ou *\"donne moi un repas de masse\"*",
    ],
}


def extract_desired_foods(message):
    # Extrait aliments demandés par le user.
    #"un repas avec du saumon et des pâtes" -> ["saumon", "pâtes"]
    match = re.search(r"avec (?:du |de la |des |le |la |les |l')?(.+)", message.lower())
    if not match:
        return []

    raw = match.group(1)
#Arrête l'extraction
    raw = re.split(r",?\s*(?:stp|svp|s'il te plait|merci|sans|pas de)\b", raw)[0]
#Sépare les aliments 
    parts = re.split(r"\s+et\s+|,\s*|\s+des\s+|\s+du\s+|\s+de la\s+", raw)
#Supp articles début
    result = []
    for part in parts:
        clean = re.sub(r"^(du |de la |des |le |la |les |l'|un |une )", "", part.strip()).strip()
        if len(clean) > 1:
            result.append(clean)
    return result


def detect_intent(message):
    # Analyse un msg pour identifier les intentions user, etourne une liste d'intentions 
    #et les données extraites 
    msg = message.lower()
    data = {}
    intents = []

    for objective in ("masse", "seche", "maintien"):
        for keyword in KEYWORDS[objective]:
            if keyword in msg:
                data["objective"] = objective
                break

    for pattern in EXCLUSION_PATTERNS:
        match = re.search(pattern, msg)
        if match:
            item = match.group(1).strip().split()[0] 
            if len(item) > 2 and item not in ("masse", "seche", "maintien"):
                data.setdefault("excluded", []).append(item)

    desired = extract_desired_foods(message)
    if desired:
        data["desired"] = desired


    is_repas = "repas" in msg or "manger" in msg or "faim" in msg

    if data.get("desired") and is_repas:
        intents.append("repas_avec")
    elif is_repas:
        intents.append("repas")

# Add l'objectif si ya pas déjà un repas
    if data.get("objective") and not intents:
        intents.append(data["objective"])

    for intent in ("seance", "tdee", "profil", "recap"):
        for keyword in KEYWORDS.get(intent, []):
            if keyword in msg and intent not in intents:
                intents.append(intent)
                break

    if not intents:
        for intent in ("greeting", "thanks", "help"):
            for keyword in KEYWORDS.get(intent, []):
                if keyword in msg:
                    return [intent], data
        return ["unknown"], data

    return intents, data


def get_response(intent):
    return random.choice(RESPONSES.get(intent, RESPONSES["unknown"]))

# smileys : ⚠️