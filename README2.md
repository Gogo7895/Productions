# NutriBot — Assistant Nutrition Discord

## Vue d'ensemble

**NutriBot** est un chatbot Discord intelligent qui génère des plans nutritionnels personnalisés en fonction des objectifs fitness de l'utilisateur (prise de masse, sèche, maintien).

**Points clés à présenter :**
- 🤖 Détection d'intention (IA avec regex + mots-clés)
- 🍽️ Génération de repas intelligente
- 📊 Calcul des macronutriments
- 👤 Système de profils utilisateur persistant
- 💾 Base de données alimentaires (API externe + fallback local)

---

## Architecture globale

```
NutriBot
├── bot/
│   └── discord_bot.py          # Cœur du bot Discord (événements, commandes)
├── chatbot/
│   ├── engine.py               # Détection d'intention + réponses prédéfinies
│   ├── meal_generator.py       # Génération de repas selon l'objectif
│   ├── nutrition.py            # Calculs TDEE + macros
│   └── profile.py              # Gestion des profils utilisateur
├── data/
│   ├── food_api.py             # Recherche d'aliments (API + fallback)
│   ├── cache.json              # Cache des requêtes API
│   ├── foods_fallback.json     # Base de données locale
│   └── workouts.json           # Programmes d'entraînement
├── storage/
│   └── users.json              # Stockage des profils
└── main.py                     # Point d'entrée
```

---

## Fonctionnalités principales

### 1️⃣ Détection d'intention (`chatbot/engine.py`)

Le bot analyse chaque message avec :
- **Mots-clés** : détection des intentions (repas, objectif, TDEE, etc.)
- **Regex** : extraction des aliments et exclusions

**Exemple :**
```
Message: "Je veux un repas avec du saumon sans poulet"
↓
Intention détectée : "repas_avec"
Données extraites :
  - desired: ["saumon"]
  - excluded: ["poulet"]
```

**Intentions supportées :**
- `repas` — génère un repas simple
- `repas_avec` — repas avec aliments spécifiques
- `masse` / `seche` / `maintien` — change l'objectif
- `tdee` — affiche les besoins caloriques
- `seance` — programme d'entraînement
- `profil` / `recap` — infos utilisateur
- `greeting` / `thanks` / `help` — réponses sociales

---

### 2️⃣ Génération de repas (`chatbot/meal_generator.py`)

Pour chaque repas généré :
1. **Calcule le TDEE** (besoins caloriques journaliers) selon :
   - Poids, taille, âge, genre, activité
   - Objectif (masse/sèche/maintien)

2. **Alloue les calories** par catégorie :
   - 40% protéines
   - 35% glucides
   - 25% lipides

3. **Sélectionne les aliments** dans la base de données
4. **Évite les exclusions** personnalisées
5. **Retourne un repas complet** avec macros calculées

---

### 3️⃣ Gestion des profils (`chatbot/profile.py`)

Chaque utilisateur a un profil sauvegardé contenant :
```json
{
  "gender": "homme",
  "weight": 75,
  "height": 180,
  "age": 25,
  "activity": "light",
  "objective": "masse",
  "excluded": ["poulet", "poisson"],
  "history": [repas générés],
  "setup_done": true
}
```

**Initialisation** : 5 questions lors du premier setup
- Genre, poids, taille, âge, activité physique

---

### 4️⃣ Système de commandes Discord

#### Commandes de repas
- `!repas [objectif]` — génère un repas
- `!seance [objectif]` — affiche un programme d'entraînement

#### Gestion du profil
- `!profil` — affiche le profil complet
- `!setpoids <kg>` — met à jour le poids
- `!setage <ans>` — met à jour l'âge
- `!setobjectif <objectif>` — change l'objectif (masse/seche/maintien)

#### Autres
- `!recap` — résumé nutritionnel (derniers repas)
- `!configuration` — reconfigurer le profil
- `!reset` — réinitialise tout
- `!aide` — affiche l'aide

---

## Points forts à mentionner à l'oral

### 🎯 Logique intelligente

1. **Détection multi-intention**
   - Un message peut contenir plusieurs intentions
   - Priorité : `repas_avec > repas > objectif > autres`

2. **Extraction intelligente d'aliments**
   - Parse "un repas avec du saumon ET des pâtes" → `["saumon", "pâtes"]`
   - Gère les variations : "de la", "du", "des", "le", "la", etc.

3. **Calcul TDEE réaliste**
   - Utilise la formule de Harris-Benedict (recommandée par l'INSERM)
   - Adapte selon l'activité physique

### 🔄 Persistance des données

- Les profils sont **sauvegardés en JSON** (`storage/users.json`)
- L'historique de repas est **stocké par utilisateur**
- Les conversations sont **gardées en mémoire** (derniers 4 messages) pour le contexte

### 🍽️ Base de données alimentaires

Stratégie à deux niveaux :
1. **API OpenFoodFacts** — accès à 500k+ aliments réels
2. **Base locale** (`foods_fallback.json`) — fallback garanti (50+ aliments)

```python
# Exemple de recherche d'aliment
search_food_by_name("saumon", "proteine")
→ {"name": "Saumon", "calories": 208, "proteins": 20, "carbs": 0, "fats": 13}
```

### 📊 Calcul des macros

Chaque repas inclut :
- Calories totales
- Protéines (g)
- Glucides (g)
- Lipides (g)
- Barre de progression vers l'objectif calorique

---

## Exemple de flux complet

### Scénario : Nouvel utilisateur

```
Utilisateur: "Salut, je veux prendre de la masse"
↓
Bot détecte: intention="masse"
✅ Lance l'initialisation (5 questions)
↓
Utilisateur répond: homme, 70kg, 175cm, 25ans, activité=light
↓
TDEE calculé: 2500 kcal/jour
↓
Génère repas de masse: 833 kcal/repas
  - Poulet (150g) + Riz (100g) + Brocoli (100g)
  - Sauvegarde dans le profil
↓
Bot: "Profil configuré! Voici ton premier repas 👇"
```

### Scénario : Repas personnalisé

```
Utilisateur: "Donne-moi un repas avec du saumon sans poulet"
↓
Bot détecte: 
  - intention="repas_avec"
  - desired=["saumon"]
  - excluded=["poulet"]
↓
Cherche saumon dans protéines ✓
Exclut le poulet
Complète avec glucides + légumes
↓
Génère repas:
  - Saumon (150g, 312 kcal, 31g prot)
  - Pâtes (100g, 131 kcal, 5g prot)
  - Salade (100g, 15 kcal, 1g prot)
```

---

## Détails techniques importants

### Stockage en JSON
```python
# users.json
{
  "123456789": {
    "gender": "homme",
    "weight": 75,
    ...
    "history": [repas1, repas2, ...]
  }
}
```

### Historique conversationnel
```python
# conversation_history
{
  "123456789": [
    "Salut",
    "Je veux un repas",
    "Avec du saumon",
    "Sans poulet"
  ]
}
```
→ Garde les **4 derniers messages** pour contexte

### Validation des entrées
- Poids : 30-300 kg
- Taille : 100-250 cm
- Âge : 10-100 ans
- Objectif : masse/seche/maintien uniquement

---

## Difficultés surmontées

1. **Parsing d'aliments complexes**
   - "un repas avec du saumon et des pâtes" → extraction correcte de `["saumon", "pâtes"]`
   - Gestion des accents et variantes

2. **Calcul TDEE précis**
   - Formule Harris-Benedict (standard fitness)
   - Adapté par coefficient d'activité

3. **Fallback API**
   - Si OpenFoodFacts ne répond pas → base locale
   - Garantit une expérience utilisateur sans interruption

4. **Gestion des exclusions**
   - Certains utilisateurs ne mangent pas de viande/poisson/etc.
   - Sauvegardées et appliquées à tous les futurs repas

5. **Intents multiples**
   - "Je veux prendre de la masse avec du saumon" → 2 intentions
   - Traitement de priorité pour éviter les doublons

---

## Comment tester en démo

### Setup initial
```
Taper: "Salut NutriBot"
→ Bot demande genre, poids, taille, âge, activité
→ Génère 1er repas
```

### Tests de repas
```
"Donne-moi un repas de sèche" → repas adapté sèche
"Un repas avec du poulet" → cherche poulet
"Sans poisson" → ajoute exclusion, met à jour profil
```

### Consultation de données
```
"!profil" → affiche le profil complet
"!tdee" → affiche besoins caloriques pour chaque objectif
"!recap" → résumé des derniers repas
```

---

## Code à montrer pendant la présentation

### Point 1 : Détection d'intention
**Fichier:** `chatbot/engine.py` (ligne 87-145)
- Montre la logique de parsing
- Extraction des mots-clés et regex

### Point 2 : Génération de repas
**Fichier:** `chatbot/meal_generator.py`
- Allocation des calories
- Sélection des aliments

### Point 3 : Gestion des événements Discord
**Fichier:** `bot/discord_bot.py` (ligne 69-198)
- `on_message` — traite chaque message
- Boucle sur les intentions
- Envoie les réponses

### Point 4 : Profil utilisateur
**Fichier:** `chatbot/profile.py`
- Chargement/sauvegarde JSON
- Historique des repas

---

## Conclusion pour l'oral

> "NutriBot est un assistant nutritionnel **complètement personnalisé** qui détecte automatiquement ce que l'utilisateur demande, génère un repas adapté à son profil et ses objectifs fitness, puis le sauvegarde. C'est un système complet qui montre la détection d'intention, la persistance des données, et l'intégration avec une API externe."

**Points clés :**
- ✅ IA : détection d'intention (mots-clés + regex)
- ✅ Algorithme : calcul TDEE + allocation macros
- ✅ Données : API alimentaires + fallback local
- ✅ Persistance : profils et historique sauvegardés
- ✅ Interface : 12+ commandes Discord complètes
- ✅ Code 100% maison (français + structure propre)
