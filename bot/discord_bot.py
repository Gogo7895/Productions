# discord_bot.py bot Discord (gestion des messages et commandes)
import json
import discord
from discord.ext import commands

from chatbot.engine import detect_intent, get_response
from chatbot.meal_generator import generate_meal, OBJECTIVES_CONFIG
from chatbot.nutrition import calculate_tdee, calculate_meal_macros
from chatbot.profile import get_profile, save_profile, add_meal_to_history
from data.food_api import search_food_by_name, get_food_for_category

DISCLAIMER = "Suggestions indicatives uniquement — Pour plus de détails, consulte un professionnel de santé."
OBJ_LABELS = {"masse": "prise de masse 💪", "seche": "sèche 🔥", "maintien": "maintien ⚖️"}

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# garde les dernier msg de chaque user pour give contexte au chatbot
conversation_history = {}

# Fonctions utilitaires

def add_to_history(user_id, text):
# Ajoute un message à l'historique et garde seulement les 4 derniers.
    uid = str(user_id)
    if uid not in conversation_history:
        conversation_history[uid] = []
    conversation_history[uid].append(text)
    conversation_history[uid] = conversation_history[uid][-4:]


def get_tdee(profile, objective=None):
# Calcule les besoins caloriques journaliers en fonction du profil.
    obj = objective or profile.get("objective") or "maintien"
    return calculate_tdee(profile["weight"], profile["age"], obj,
                          profile["activity"], profile["height"], profile["gender"])


def apply_exclusions(profile, user_id, excluded_list):
# Enregistre les aliments à éviter et sauvegarde le profil.
    for exc in excluded_list:
        if exc not in profile["excluded"]:
            profile["excluded"].append(exc)
    save_profile(user_id, profile)


async def check_setup(channel, user, profile):
# Vérifie que le profil est configuré, sinon lance les 5 questions d'initialisation.
    if profile.get("setup_done"):
        return True
    await channel.send("J'ai besoin de te connaître un peu mieux d'abord ! ")
    await run_initialization(channel, user, profile)
    return False


# Events

@bot.event
async def on_ready():
    print(f"NutriBot connecté : {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="tes macros | !aide"
    ))


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
    if message.content.startswith("!"):
        return

    user_id = str(message.author.id)
    add_to_history(user_id, message.content)
    intents, data = detect_intent(message.content)
    profile = get_profile(user_id)

# Traite chaque intention détectée (un message peut avoir plusieurs intentions)
    for intent in intents:

# ── Repas avec aliments spécifiques ("un repas avec du saumon sans poulet") ──
        if intent == "repas_avec":
            if not await check_setup(message.channel, message.author, profile):
                continue

            if data.get("excluded"):
                apply_exclusions(profile, user_id, data["excluded"])

            obj = profile.get("objective") or "maintien"
            tdee = get_tdee(profile, obj)

# Cherche les aliments spécifiques que l'utilisateur a demandés
            foods = {}
            for food_name in data.get("desired", []):
                for cat in ["proteine", "glucide", "legume"]:
                    if cat not in foods:
                        found = search_food_by_name(food_name, cat)
                        if found:
                            found["qty"] = 150 if cat == "proteine" else 100
                            foods[cat] = found
                            break

# Remplit les catégories manquantes avec des aliments aléatoires
            for cat in ["proteine", "glucide", "legume"]:
                if cat not in foods:
                    food = get_food_for_category(cat, profile["excluded"])
                    if food:
                        foods[cat] = food

            meal = {
                "foods": foods,
                "macros": calculate_meal_macros(list(foods.values())),
                "config": OBJECTIVES_CONFIG.get(obj, OBJECTIVES_CONFIG["maintien"]),
                "tdee": tdee, "meal_target": tdee // 3,
            }
            add_meal_to_history(user_id, meal)

# Confirme le repas à l'utilisateur
            names = [f["name"] for f in foods.values()]
            msg = f"J'ai trouvé un repas avec : **{', '.join(names)}** 🍽️" 
            if data.get("excluded"):
                msg += f" (sans {', '.join(data['excluded'])})"
            await message.channel.send(msg)
            await message.channel.send(embed=build_meal_embed(meal, message.author.display_name))

# Repas simple ("j'ai faim", "donne moi un repas") 
        elif intent == "repas":
            if not await check_setup(message.channel, message.author, profile):
                continue

            if data.get("objective"):
                profile["objective"] = data["objective"]
            if data.get("excluded"):
                apply_exclusions(profile, user_id, data["excluded"])
                await message.channel.send(f"Noté : sans **{', '.join(data['excluded'])}** 👍")

            obj = profile.get("objective") or "maintien"
            meal = generate_meal(obj, profile["excluded"], get_tdee(profile, obj))
            add_meal_to_history(user_id, meal)
            await message.channel.send("Voilà ce que je te propose 🍽️")
            await message.channel.send(embed=build_meal_embed(meal, message.author.display_name))

# Objectif (masse / sèche / maintien)
        elif intent in ("masse", "seche", "maintien"):
            if not await check_setup(message.channel, message.author, profile):
                profile["objective"] = intent
                save_profile(user_id, profile)
                continue

            await message.channel.send(f"Tu veux passer en **{OBJ_LABELS[intent]}** ? Je te prépare un repas !")
            profile["objective"] = intent
            save_profile(user_id, profile)

            meal = generate_meal(intent, profile["excluded"], get_tdee(profile, intent))
            add_meal_to_history(user_id, meal)
            await message.channel.send(embed=build_meal_embed(meal, message.author.display_name))

# TDEE / besoins caloriques
        elif intent == "tdee":
            if not await check_setup(message.channel, message.author, profile):
                continue

            embed = discord.Embed(
                title="🔥 Tes besoins caloriques journaliers",
                description=f"Pour {profile['weight']}kg, {profile['height']}cm, {profile['age']}ans",
                color=0x3498DB,
            )
            for obj, label in OBJ_LABELS.items():
                tdee = get_tdee(profile, obj)
                embed.add_field(name=label, value=f"**{tdee} kcal/jour**\n~{tdee // 3} kcal/repas", inline=True)
            embed.set_footer(text=DISCLAIMER)
            await message.channel.send(embed=embed)

# Profil
        elif intent == "profil":
            await cmd_profil(await bot.get_context(message))

# Séance
        elif intent == "seance":
            await cmd_seance(await bot.get_context(message))

# Recap
        elif intent == "recap":
            await cmd_recap(await bot.get_context(message))

# Cas spécial : l'utilisateur ajoute juste une exclusion alimentaire
        elif data.get("excluded") and intent == "unknown":
            apply_exclusions(profile, user_id, data["excluded"])
            items = ", ".join(data["excluded"])
            await message.channel.send(f"Noté ! Je retire **{items}** de tes suggestions 👍\n\n{DISCLAIMER}")

# Réponses sociales prédéfinies (salutations, remerciements, aide, etc.)
        else:
            await message.channel.send(get_response(intent))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Commande inconnue. Tape `!aide` pour l'aide.\n\n{DISCLAIMER}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Argument manquant : `{ctx.prefix}{ctx.command} {ctx.command.signature}`")
    else:
        await ctx.send(f"Erreur : {error}")


# Commandes !

@bot.command(name="repas", aliases=["manger"])
async def cmd_repas(ctx, objectif=None):
    profile = get_profile(str(ctx.author.id))
    obj = (objectif or profile.get("objective") or "maintien").lower()
    if obj not in OBJECTIVES_CONFIG:
        await ctx.send(f"Objectif non reconnu (`masse`, `seche`, `maintien`).\n\n{DISCLAIMER}")
        return
    async with ctx.typing():
        meal = generate_meal(obj, profile["excluded"], get_tdee(profile, obj))
        add_meal_to_history(str(ctx.author.id), meal)
    await ctx.send(embed=build_meal_embed(meal, ctx.author.display_name))


@bot.command(name="seance", aliases=["séance", "entraînement"])
async def cmd_seance(ctx, objectif=None):
    profile = get_profile(str(ctx.author.id))
    obj = (objectif or profile.get("objective") or "maintien").lower()
    if obj not in OBJECTIVES_CONFIG:
        await ctx.send(f"Objectif non reconnu (`masse`, `seche`, `maintien`).\n\n{DISCLAIMER}")
        return
    try:
        with open("data/workouts.json", "r", encoding="utf-8") as f:
            program = json.load(f).get(obj)
    except Exception as e:
        await ctx.send(f"Erreur chargement programme : {e}")
        return
    if not program:
        await ctx.send(f"Programme non disponible pour `{obj}`.")
        return

    config = OBJECTIVES_CONFIG[obj]
    embed = discord.Embed(
        title=f"Programme — {program['label']}",
        description=f"**Fréquence :** {program['frequency']} · ~{program['calories_burned']} kcal/séance",
        color=config["color"]
    )
    for session in program.get("sessions", []):
        text = ""
        for ex in session.get("exercises", []):
            text += f"• **{ex['name']}** — {ex['sets']}×{ex['reps']} (repos {ex['rest']})\n"
        embed.add_field(name=f"{session['day']} — {session['focus']}", value=text or "—", inline=False)
    embed.set_footer(text=f"{program['tip']} • {DISCLAIMER}")
    await ctx.send(embed=embed)


@bot.command(name="profil", aliases=["moi"])
async def cmd_profil(ctx):
    profile = get_profile(str(ctx.author.id))
    obj = profile.get("objective") or "Non défini"
    config = OBJECTIVES_CONFIG.get(obj, {})

    embed = discord.Embed(title=f"Profil de {ctx.author.display_name}", color=config.get("color", 0x95A5A6))
    embed.add_field(name="Objectif", value=config.get("label", obj), inline=True)
    embed.add_field(name="Genre", value=profile["gender"].capitalize(), inline=True)
    embed.add_field(name="Poids", value=f"{profile['weight']} kg", inline=True)
    embed.add_field(name="Taille", value=f"{profile['height']} cm", inline=True)
    embed.add_field(name="Âge", value=f"{profile['age']} ans", inline=True)
    embed.add_field(name="Activité", value=profile["activity"], inline=True)
    embed.add_field(name="TDEE", value=f"~{get_tdee(profile)} kcal/jour", inline=True)
    excluded = profile.get("excluded", [])
    embed.add_field(name="Exclusions", value=", ".join(excluded) if excluded else "Aucune", inline=False)
    embed.set_footer(text=DISCLAIMER)
    await ctx.send(embed=embed)


@bot.command(name="setpoids")
async def cmd_setpoids(ctx, poids: float):
    if not (30 <= poids <= 300):
        return await ctx.send(f"Poids invalide (30-300 kg).\n\n{DISCLAIMER}")
    profile = get_profile(str(ctx.author.id))
    profile["weight"] = poids
    save_profile(str(ctx.author.id), profile)
    await ctx.send(f"Poids mis à jour : **{poids} kg**\n\n{DISCLAIMER}")


@bot.command(name="setage")
async def cmd_setage(ctx, age: int):
    if not (10 <= age <= 100):
        return await ctx.send(f"Âge invalide (10-100 ans).\n\n{DISCLAIMER}")
    profile = get_profile(str(ctx.author.id))
    profile["age"] = age
    save_profile(str(ctx.author.id), profile)
    await ctx.send(f"Âge mis à jour : **{age} ans**\n\n{DISCLAIMER}")


@bot.command(name="setobjectif", aliases=["objectif"])
async def cmd_setobjectif(ctx, objectif: str):
    obj = objectif.lower()
    if obj not in OBJECTIVES_CONFIG:
        return await ctx.send(f"Objectif non reconnu (`masse`, `seche`, `maintien`).\n\n{DISCLAIMER}")
    profile = get_profile(str(ctx.author.id))
    profile["objective"] = obj
    save_profile(str(ctx.author.id), profile)
    await ctx.send(f"Objectif défini : **{OBJECTIVES_CONFIG[obj]['label']}**\n\n{DISCLAIMER}")


@bot.command(name="récapitulatif", aliases=["récap", "bilan", "historique"])
async def cmd_recap(ctx):
    profile = get_profile(str(ctx.author.id))
    history = profile.get("history", [])
    if not history:
        return await ctx.send(f"Aucun repas enregistré. Tape `!repas` !\n\n{DISCLAIMER}")

    total_cal = sum(m["macros"].get("calories", 0) for m in history)
    total_prot = sum(m["macros"].get("proteins", 0) for m in history)

    embed = discord.Embed(title="Résumé nutritionnel", description=f"**{len(history)} derniers repas**", color=0x3498DB)
    embed.add_field(name="Moy. calories/repas", value=f"{round(total_cal / len(history))} kcal", inline=True)
    embed.add_field(name="Moy. protéines/repas", value=f"{round(total_prot / len(history), 1)}g", inline=True)
    embed.set_footer(text=DISCLAIMER)
    await ctx.send(embed=embed)


@bot.command(name="reset")
async def cmd_reset(ctx):
    from chatbot.profile import DEFAULTS
    save_profile(str(ctx.author.id), dict(DEFAULTS))
    await ctx.send(f"Profil réinitialisé ! Dis-moi ton objectif.\n\n{DISCLAIMER}")


@bot.command(name="aide")
async def cmd_aide(ctx):
    await ctx.send(get_response("help"))


@bot.command(name="configuration", aliases=["initialisation", "paramètres"])
async def cmd_setup(ctx):
    await run_initialization(ctx.channel, ctx.author, get_profile(str(ctx.author.id)))


#Initialisation (5 questions pour configurer le profil)

async def ask_question(channel, user, question):
    # Pose une question et attend la réponse (délai 60s).
    await channel.send(question)
    msg = await bot.wait_for("message", check=lambda m: m.author == user and m.channel == channel, timeout=60)
    return msg.content


def extract_number(text, allow_dot=True):
    # Extrait un nombre d'un texte.
    chars = ""
    for c in text:
        if c.isdigit() or (c == "." and allow_dot):
            chars += c
    return float(chars) if chars else 0


async def run_initialization(channel, user, profile):
    # Pose 5 questions pour configurer le profil.
    try:
# 1. Genre
        resp = await ask_question(channel, user,
            f"👋 **Bienvenue {user.display_name} !**\n\n**1/5 — Genre** : `homme` ou `femme` ?")
        gender = "femme" if "femme" in resp.lower() else "homme"

# 2. Poids
        resp = await ask_question(channel, user, "**2/5 — Poids** en kg ? *(ex: 75)*")
        weight = extract_number(resp)
        if not (30 <= weight <= 300):
            raise ValueError("Poids invalide")

# 3. Taille
        resp = await ask_question(channel, user, "**3/5 — Taille** en cm ? *(ex: 175)*")
        height = extract_number(resp)
        if not (100 <= height <= 250):
            raise ValueError("Taille invalide")

# 4. Âge
        resp = await ask_question(channel, user, "**4/5 — Âge** ? *(ex: 22)*")
        age = int(extract_number(resp, allow_dot=False))
        if not (10 <= age <= 100):
            raise ValueError("Âge invalide")

# 5. Activité
        resp = await ask_question(channel, user,
            "**5/5 — Activité** :\n• `sédentaire` — peu de sport\n• `léger` — 1-3×/sem\n"
            "• `modéré` — 3-5×/sem\n• `actif` — 6-7×/sem")
        resp_lower = resp.lower()
        if "sédentaire" in resp_lower or "sedentary" in resp_lower:
            activity = "sedentaire"
        elif "léger" in resp_lower or "light" in resp_lower:
            activity = "léger"
        elif "actif" in resp_lower or "active" in resp_lower:
            activity = "actif"
        else:
            activity = "modéré"

    except Exception:
        await channel.send("❌ Erreur ou temps écoulé. Tape `!setup` pour recommencer.")
        return

# Sauvegarder le profil
    profile.update({"gender": gender, "weight": weight, "height": height,
                    "age": age, "activity": activity, "setup_done": True})
    save_profile(str(user.id), profile)

# Afficher le récap
    obj = profile.get("objective") or "maintien"
    tdee = calculate_tdee(weight, age, obj, activity, height, gender)

    embed = discord.Embed(title="✅ Profil configuré !", color=0x2ECC71)
    embed.add_field(name="Genre", value=gender.capitalize(), inline=True)
    embed.add_field(name="Poids", value=f"{weight} kg", inline=True)
    embed.add_field(name="Taille", value=f"{height} cm", inline=True)
    embed.add_field(name="Âge", value=f"{age} ans", inline=True)
    embed.add_field(name="Activité", value=activity, inline=True)
    embed.add_field(name=f"🔥 TDEE ({obj})", value=f"**{tdee} kcal/jour** (~{tdee // 3}/repas)", inline=False)
    embed.set_footer(text=DISCLAIMER)
    await channel.send(embed=embed)

# Premier repas automatique
    meal = generate_meal(obj, profile.get("excluded", []), tdee)
    add_meal_to_history(str(user.id), meal)
    await channel.send("Voici ton premier repas", embed=build_meal_embed(meal, user.display_name))


# Construction de l'embed repas 

CAT_LABELS = {"proteine": "🥩 Protéine", "glucide": "🌾 Glucide", "legume": "🥦 Légume"}

def build_meal_embed(meal, username):
    # Crée l'embed Discord pour afficher un repas.
    config = meal["config"]
    macros = meal["macros"]
    target = meal["meal_target"]

    embed = discord.Embed(
        title=f"🍽️ Repas suggéré — {config['label']}",
        description=f"Pour **{username}**",
        color=config["color"]
    )

# Afficher chaque aliment
    for cat, food in meal["foods"].items():
        qty = food.get("qty", 100)
        cal = round(food.get("calories", 0) * qty / 100)
        prot = round(food.get("proteins", 0) * qty / 100, 1)
        icon = "🌐" if food.get("source") == "OpenFoodFacts" else "📦"
        embed.add_field(
            name=f"{CAT_LABELS.get(cat, cat)} {icon}",
            value=f"**{food['name']}** — {qty}g\n`{cal} kcal · {prot}g prot`",
            inline=False
        )

# Total macros
    embed.add_field(name="Total", value=(
        f"**{macros['calories']} kcal** · {macros['proteins']}g prot · "
        f"{macros['carbs']}g glu · {macros['fats']}g lip"
    ), inline=False)

# Barre de progression
    ratio = min(macros["calories"] / max(target, 1), 1.0)
    filled = int(ratio * 10)
    bar = "█" * filled + "░" * (10 - filled)
    embed.add_field(name=f"Objectif (~{target} kcal)", value=f"`{bar}` {int(ratio * 100)}%", inline=False)

    embed.set_footer(text=f"{config['tip']} • {DISCLAIMER}")
    return embed

# smileys : 💪🔥⚖️🍽️👍👋❌✅🥩🥦🌐📦█░