import os
import joblib

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "fraud_model.pkl"
)

model = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)


def analyze(transaction):

    if model is None:
        return 75

    try:
        prediction = model.predict([transaction])

        return int(prediction[0])

    except Exception:
        return 75