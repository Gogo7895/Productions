import pickle
import os

_pipeline = None
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "classifier.pkl")
CONFIDENCE_THRESHOLD = 0.45


def _load_model():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if not os.path.exists(_MODEL_PATH):
        raise FileNotFoundError(
            "Modèle non trouvé. Lance python ml/train.py d'abord."
        )
    with open(_MODEL_PATH, "rb") as f:
        _pipeline = pickle.load(f)
    return _pipeline


def predict_intent(text: str) -> tuple[str, float]:
 # Prédit l'intention d'un texte. Retourne (tag, confidence).
    try:
        model = _load_model()
        probas = model.predict_proba([text])[0]
        confidence = float(max(probas))
        if confidence < CONFIDENCE_THRESHOLD:
            return "unknown", confidence
        label = model.predict([text])[0]
        return label, confidence
    except FileNotFoundError as e:
        print(f"[ML] {e}")
        return "unknown", 0.0
    except Exception as e:
        print(f"[ML] Erreur de prédiction : {e}")
        return "unknown", 0.0


if __name__ == "__main__":
    test_phrases = [
        "je veux prendre de la masse",
        "je veux maigrir rapidement",
        "salut comment ça va",
        "je n'aime pas le thon",
        "montre moi mon bilan de la semaine",
        "azertyuiop qsdfghjklm",
    ]
    print("=== Tests de prédiction ML ===")
    for phrase in test_phrases:
        intent, conf = predict_intent(phrase)
        print(f"  '{phrase}' → {intent} ({conf:.2f})")
