# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# import joblib
# import numpy as np
# from pymongo import MongoClient
#
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all requests
#
# # Load the trained KNN model, scaler, and encoders
# knn_model = joblib.load("knn_model.pkl")  # ✅ Load KNN model
# scaler = joblib.load("scaler.pkl")  # ✅ Load Scaler
# specialization_encoder = joblib.load("label_encoder_specialization.pkl")  # ✅ Encode Specializations
# district_encoder = joblib.load("label_encoder_district.pkl")  # ✅ Encode Districts
#
# # Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
# MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
# client = MongoClient(MONGO_URI)
# db = client["HopeBridge"]  # ✅ Ensure database is HopeBridge
# treatment_collection = db["Recommendations"]  # ✅ Ensure collection is Recommendations
# doctor_collection = db["Doctors"]  # ✅ Ensure Doctors collection is referenced
#
# @app.route("/treatment")
# def treatment_page():
#     return render_template("treatment.html")  # Serves treatment.html
#
# @app.route("/get_doctors", methods=["POST"])
# def get_doctors():
#     try:
#         data = request.json
#         specialization = data.get("specialization", "").strip()
#         district = data.get("district", "").strip()
#
#         # Validate input
#         if not specialization or not district:
#             return jsonify({"error": "Missing specialization or district"}), 400
#
#         # Use the exact field names from MongoDB (with spaces)
#         query = {
#             "specialization": {"$regex": f"^{specialization} *$", "$options": "i"},
#             "district ": {"$regex": f"^{district} *$", "$options": "i"}
#         }
#
#         # Fetch doctors from MongoDB
#         doctors = list(db["Recommendations"].find(query, {"_id": 0}))
#
#         if not doctors:
#             return jsonify({"message": "No doctors found"}), 404
#
#         return jsonify(doctors), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import joblib
import numpy as np
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_session import Session
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all requests

# Configure Flask Session
app.config["SECRET_KEY"] = "supersecretkey"  # Change this to a more secure key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
mongo = PyMongo(app)

db = mongo.db  # Database Reference
users_collection = db.users  # User authentication
screen_test_collection = db.ScreenTest  # ScreenTest answers and risk levels
treatment_collection = db.Recommendations  # Treatment recommendations
doctor_collection = db.Doctors  # Doctor list

# Load trained KNN model, scaler, and encoders
knn_model = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\knn_model.pkl")
scaler = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\scaler.pkll")
specialization_encoder = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\label_encoder_specialization.pkl")
district_encoder = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\label_encoder_district.pkl")

# ------------------- User Authentication -------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Check if user exists
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User does not exist"}), 401

    # Verify password
    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Store user in session
    session["user_email"] = email

    return jsonify({"message": "Login successful", "email": email}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_email", None)
    return jsonify({"message": "Logged out successfully"}), 200

# ------------------- ScreenTest Submission -------------------
@app.route('/submit', methods=['POST'])
def submit_answers():
    # Ensure user is logged in
    if "user_email" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json  # Get submitted answers
    user_email = session["user_email"]  # Retrieve logged-in user

    scores = {
        "All of the time": 4,
        "Most of the time": 3,
        "Some of the time": 2,
        "A little of the time": 1,
        "None of the time": 0,
        "Yes": 10,
        "No": 0
    }

    # Calculate total score
    total_score = sum(scores.get(answer, 0) for answer in data.values())

    # Determine the risk level
    if total_score >= 35:
        risk_level = "High"
    elif total_score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # Store the answers and risk level in MongoDB under a single collection
    try:
        screen_test_collection.insert_one({
            "user_email": user_email,  # Link responses to logged-in user
            "screen_answers": data,
            "risk_level": risk_level
        })
        return jsonify({"message": "Answers received and risk level calculated!", "risk_level": risk_level}), 200
    except Exception as e:
        print("Error saving to MongoDB:", e)
        return jsonify({"error": "Failed to save data!"}), 500

# ------------------- Fetch User's ScreenTest History -------------------
@app.route('/user/tests', methods=['GET'])
def get_user_tests():
    # Ensure user is logged in
    if "user_email" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_email = session["user_email"]

    # Retrieve all test results of the logged-in user
    user_tests = list(screen_test_collection.find({"user_email": user_email}, {"_id": 0}))  # Exclude MongoDB ID

    return jsonify({"tests": user_tests}), 200

# ------------------- Doctor Recommendation -------------------
@app.route("/get_doctors", methods=["POST"])
def get_doctors():
    try:
        data = request.json
        specialization = data.get("specialization", "").strip()
        district = data.get("district", "").strip()

        # Validate input
        if not specialization or not district:
            return jsonify({"error": "Missing specialization or district"}), 400

        # Use exact field names from MongoDB (fixing space issue)
        query = {
            "specialization": {"$regex": f"^{specialization}$", "$options": "i"},
            "district": {"$regex": f"^{district}$", "$options": "i"}  # Fixed key (removed space)
        }

        # Fetch doctors from MongoDB
        doctors = list(doctor_collection.find(query, {"_id": 0}))

        if not doctors:
            return jsonify({"message": "No doctors found"}), 404

        return jsonify(doctors), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------- Treatment Page -------------------
@app.route("/treatment")
def treatment_page():
    return render_template("treatment.html")  # Serves treatment.html

if __name__ == "__main__":
    app.run(debug=True, port=5000)

