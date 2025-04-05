from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
# Connect to MongoDB Atlas


MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["HopeBridge"]  
treatment_collection = db["Recommendations"]  
doctor_collection = db["Doctors"] 
users_collection = db['users']  # Assuming user age is in the 'users' collection

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

# Define specialization mapping
age_risk_specializations = {
    "below_13": {
        "Low Risk": [
            "Child Psychologist", "Child Psychology", "Counsellor", "Art Therapist"
        ],
        "Moderate Risk": [
            "Child and Adolescent Psychologist", "Child Counselling Psychologist and Therapist",
            "Mental Health Counselor", "Counseling Psychologist"
        ],
        "High Risk": [
            "Child Psychiatrist", "Paediatric Psychiatrist", "Consultant Paediatric Neurologist",
            "Clinical Psychologist"
        ]
    },
    "above_13": {
        "Low Risk": [
            "Counseling Psychologist", "Counselor", "Art Therapist", "End of life care"
        ],
        "Moderate Risk": [
            "Applied Psychologist", "Behaviour Therapist", "Cognitive Behavioral Therapy",
            "Psychological Counselling"
        ],
        "High Risk": [
            "Psychiatrist", "Consultant Neurologist", "Clinical Psychologist", "Clinical Neurologist",
            "Addiction Professional"
        ]
    }
}

@app.route("/get_risk", methods=["GET"])
def get_risk():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_data = treatment_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not user_data:
        return jsonify({"error": "User risk data not found"}), 404

    # 👉 Force FaceRecognition score to low (1)
    user_data["FaceRecognition"] = 1

    user_profile = users_collection.find_one({"user_id": user_id}, {"age": 1, "_id": 0})
    if not user_profile or "age" not in user_profile:
        return jsonify({"error": "User age data not found"}), 404

    age = user_profile["age"]
    age_group = "below_13" if age < 13 else "above_13"

    risk_score = calculate_final_risk(user_data)
    risk_level = get_risk_level(risk_score)
    recommended_specializations = age_risk_specializations.get(age_group, {}).get(risk_level, [])

    response = {
        "user_id": user_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "age": age,
        "age_group": age_group,
        "recommended_specializations": recommended_specializations,
        "components": user_data
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
