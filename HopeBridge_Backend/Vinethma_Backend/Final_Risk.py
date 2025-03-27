from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)

# Connect to MongoDB Atlas
MONGO_URI = "your_mongodb_uri"
client = MongoClient(MONGO_URI)
db = client['your_database']
collection = db['risk_levels']

# Define weights for risk components
WEIGHTS = {
    "ScreenTest": 0.3,
    "JournalEntries": 0.2,
    "FaceRecognition": 0.3,
    "ChatbotAnalysis": 0.2
}

# Define risk thresholds
RISK_THRESHOLDS = [
    (0, 3, "Low Risk"),
    (4, 6, "Moderate Risk"),
    (7, 10, "High Risk")
]


def calculate_final_risk(scores):
    """Calculate final risk score based on component weights."""
    final_score = sum(scores[comp] * WEIGHTS.get(comp, 0) for comp in scores)
    return round(final_score, 2)


def get_risk_level(score):
    """Get risk level based on score."""
    for low, high, level in RISK_THRESHOLDS:
        if low <= score <= high:
            return level
    return "Unknown Risk Level"


@app.route("/get_risk", methods=["GET"])
def get_risk():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_data = collection.find_one({"user_id": user_id}, {"_id": 0})
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    risk_score = calculate_final_risk(user_data)
    risk_level = get_risk_level(risk_score)

    response = {
        "user_id": user_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "components": user_data
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
