from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pymongo import MongoClient

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all requests

# Load the trained KNN model, scaler, and encoders
knn_model = joblib.load("knn_model.pkl")  # ✅ Load KNN model
scaler = joblib.load("scaler.pkl")  # ✅ Load Scaler
specialization_encoder = joblib.load("label_encoder_specialization.pkl")  # ✅ Encode Specializations
district_encoder = joblib.load("label_encoder_district.pkl")  # ✅ Encode Districts

# Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["HopeBridge"]  # ✅ Ensure database is HopeBridge
treatment_collection = db["Recommendations"]  # ✅ Ensure collection is Recommendations
doctor_collection = db["Doctors"]  # ✅ Ensure Doctors collection is referenced

@app.route("/treatment")
def treatment_page():
    return render_template("treatment.html")  # Serves treatment.html

@app.route("/get_doctors", methods=["POST"])
def get_doctors():
    try:
        data = request.json
        specialization = data.get("specialization", "").strip()
        district = data.get("district", "").strip()

        # Validate input
        if not specialization or not district:
            return jsonify({"error": "Missing specialization or district"}), 400

        # Use the exact field names from MongoDB (with spaces)
        query = {
            "specialization": {"$regex": f"^{specialization} *$", "$options": "i"},
            "district ": {"$regex": f"^{district} *$", "$options": "i"}
        }

        # Fetch doctors from MongoDB
        doctors = list(db["Recommendations"].find(query, {"_id": 0}))

        if not doctors:
            return jsonify({"message": "No doctors found"}), 404

        return jsonify(doctors), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
