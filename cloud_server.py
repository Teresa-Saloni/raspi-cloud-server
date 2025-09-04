from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier

# ==========================
# Setup
# ==========================
app = Flask(__name__)

# Secret key for encryption (keep same on Raspberry Pi and Cloud)
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())
fernet = Fernet(SECRET_KEY.encode())

# Storage
DATA_FILE = "sensor_data.csv"
MODEL_FILE = "model.pkl"

# ==========================
# Routes
# ==========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Raspberry Pi Cloud Server is running 🚀",
        "upload_endpoint": "/upload",
        "train_endpoint": "/train"
    })

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        encrypted = data.get("payload", "")

        # Decrypt
        decrypted = fernet.decrypt(encrypted.encode()).decode()
        temp, hum, label = decrypted.split(",")

        # Save into CSV
        df = pd.DataFrame([[float(temp), float(hum), label]],
                          columns=["temperature", "humidity", "label"])
        if not os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, index=False)
        else:
            df.to_csv(DATA_FILE, mode="a", header=False, index=False)

        return jsonify({"status": "success", "message": "Data stored ✅"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/train", methods=["POST"])
def train():
    try:
        if not os.path.exists(DATA_FILE):
            return jsonify({"status": "error", "message": "No data available"})

        # Load dataset
        df = pd.read_csv(DATA_FILE)
        X = df[["temperature", "humidity"]]
        y = df["label"]

        # Train ML model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Save model
        joblib.dump(model, MODEL_FILE)

        return jsonify({"status": "success", "message": "Model trained ✅"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if not os.path.exists(MODEL_FILE):
            return jsonify({"status": "error", "message": "Model not trained yet"})

        model = joblib.load(MODEL_FILE)

        data = request.json
        temp = float(data.get("temperature"))
        hum = float(data.get("humidity"))

        pred = model.predict([[temp, hum]])[0]

        return jsonify({"status": "success", "prediction": pred})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ==========================
# Run
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
