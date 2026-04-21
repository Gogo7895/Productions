import json
import pickle
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def train():
# Charge et entraîne le modèle
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    labels = []
    for intent in data["intents"]:
        for example in intent["examples"]:
            texts.append(example)
            labels.append(intent["tag"])

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            analyzer="char_wb",
            min_df=1,
            max_features=5000
        )),
        ("clf", LogisticRegression(
            max_iter=2000,
            C=2.0,
            multi_class="multinomial",
            solver="lbfgs"
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred))

    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "classifier.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\n Modèle sauvegardé dans {model_path}")

    print("\n=== Tests de prédiction ===")
    test_phrases = [
# Prise de masse
        "je veux prendre de la masse",
        "objectif bulk pour moi",
        "je veux gagner du muscle",
        "je fais de la musculation pour grossir",
        "mon but c est de devenir plus costaud",
        "prise de masse musculaire svp",
        "comment je peux grossir rapidement",
        "je veux augmenter ma masse",

# Sèche
        "je veux maigrir",
        "objectif sèche",
        "je veux perdre du poids",
        "comment brûler des graisses",
        "je suis en phase de sèche",
        "je veux perdre 5 kilos",
        "perdre du ventre c est mon objectif",
        "je veux être plus sec et musclé",

# Maintien
        "je veux maintenir mon poids",
        "objectif maintien",
        "juste manger équilibré",
        "je cherche l équilibre alimentaire",
        "je veux garder ma forme actuelle",
        "pas de prise de masse ni de sèche",
        "rester stable c est mon but",
        "manger sainement sans régime",

# Exclusion
        "je n'aime pas le poulet",
        "je suis végétarien",
        "sans gluten svp",
        "pas de viande rouge",
        "je suis allergique aux noix",
        "enlève le brocoli de mon repas",
        "pas de produits laitiers",
        "retirer le saumon stp",
        "je déteste le thon",
        "je suis vegan",

# phrase politesse 
        "salut comment tu vas",
        "bonjour",
        "coucou ça roule",
        "hey yo comment ça va",
        "bonsoir nutribot",
        "salut toi",
        "hello c est moi",
        "wsh la forme",

# Bilan
        "montre moi mon bilan",
        "résumé nutrition",
        "qu est ce que j ai mangé cette semaine",
        "afficher mon historique",
        "mes stats",
        "bilan de la journée",
        "voir mon récap nutritionnel",
        "mes calories totales",

# aide
        "aide moi",
        "comment ça marche",
        "que sais tu faire",
        "tes commandes",
        "je suis perdu",
        "aide utilisation",
        "comment je t utilise",
        "donne moi les commandes",

# Phrases full
        "je veux un repas de seche avec du saumon et du riz sans brocoli",
        "je cherche une diète de prise de masse sans produits laitiers",
        "je vais m entrainer à la muscu pour prendre du muscle",
        "comment manger sainement en maintien calorique",
        "je veux perdre du gras sans perdre du muscle",
        "montre moi un plan alimentaire pour la sèche",
        "aide moi à trouver un repas équilibré",
    ]
    for phrase in test_phrases:
        pred = pipeline.predict([phrase])[0]
        proba = max(pipeline.predict_proba([phrase])[0])
        print(f"  '{phrase}' → {pred} ({proba:.2f})")


if __name__ == "__main__":
    train()
