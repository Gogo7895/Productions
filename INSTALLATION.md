# Guide de démarrage — NutriBot

## ⚡ Installation et démarrage

---

## 1️⃣ Créer et activer l'environnement virtuel

```bash
cd nutribot
python3 -m venv venv
source venv/bin/activate
```

**Sur Windows :**
```bash
cd nutribot
python -m venv venv
venv\Scripts\activate
```

---

## 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configurer le token Discord

Crée un fichier `.env` dans le dossier `nutribot/` :

```bash
echo "DISCORD_TOKEN=ton_token_discord_ici" > .env
```

**Remplace `ton_token_discord_ici` par ton vrai token Discord**

---

## 4️⃣ Lancer le bot

```bash
python main.py
```

Tu devrais voir :
```
NutriBot connecté : NutriBot#1234
```

✅ Le bot est en ligne !

---

## 🎮 Tester le bot sur Discord

```
!aide              # Affiche l'aide
!repas             # Génère un repas
!profil            # Affiche ton profil
```

Ou en message naturel :
```
Salut NutriBot
Je veux prendre de la masse
Donne-moi un repas avec du saumon
```

---

## 🚀 Prêt pour la présentation !
