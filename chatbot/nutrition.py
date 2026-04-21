#Calcul TDEE et macros (formule Mifflin-St Jeor)
#niveau d'activité 
ACTIVITY_FACTORS = {
    "sedentaire": 1.2, 
    "léger": 1.375, 
    "modéré": 1.55, 
    "actif": 1.725, 
}

# Ajust TDEE selon objectif
OBJECTIVE_FACTORS = {
    "masse": 1.15,
    "seche": 0.82,
    "maintien": 1.0, 
}


def calculate_tdee(weight, age, objective, activity="modéré", height=175, gender="homme"):
# Calcule besoins kcal journaliers (TDEE) avec Mifflin-St Jeor.
# Ajuste pour activité physique et l'objectif sport.
# Calcule métabolisme de base (BMR) Mifflin-St Jeor
    offset = 5 if gender == "homme" else -161
    bmr = 10 * weight + 6.25 * height - 5 * age + offset

    tdee = bmr * ACTIVITY_FACTORS.get(activity, 1.55)
    return int(tdee * OBJECTIVE_FACTORS.get(objective, 1.0))

def calculate_meal_macros(foods):
    total = {"calories": 0, "proteins": 0, "carbs": 0, "fats": 0}

    for food in foods:
# facteur proportionnalité pour mettre tout sur 100g
        factor = food.get("qty", 100) / 100
        for key in total:
            total[key] += food.get(key, 0) * factor

    return {k: round(v, 1) for k, v in total.items()}
