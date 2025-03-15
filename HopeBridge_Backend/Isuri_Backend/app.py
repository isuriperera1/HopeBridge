from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pymongo import MongoClient
from werkzeug.security import check_password_hash

from HopeBridge_Backend.Vinethma_Backend.Login import users_collection

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all requests

<<<<<<< HEAD

# Load the trained KNN model, scaler, and encoders

# Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
#client = MongoClient(MONGO_URI)
#db = client["HopeBridge"]  # ✅ Ensure database is HopeBridge
#treatment_collection = db["Recommendations"]  # ✅ Ensure collection is Recommendations
#doctor_collection = db["Doctors"]  # ✅ Ensure Doctors collection is referenced
#



# Configure Flask Session
app.config["SECRET_KEY"] = "supersecretkey"  # Change this to a more secure key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
=======
# Load the trained KNN model, scaler, and encoders
knn_model = joblib.load("knn_model.pkl")  # ✅ Load KNN model
scaler = joblib.load("scaler.pkl")  # ✅ Load Scaler
specialization_encoder = joblib.load("label_encoder_specialization.pkl")  # ✅ Encode Specializations
district_encoder = joblib.load("label_encoder_district.pkl")  # ✅ Encode Districts
>>>>>>> 918adbc32473d01b606ca34ac5cc12f81a2f7e49

# Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["HopeBridge"]  # ✅ Ensure database is HopeBridge
treatment_collection = db["Recommendations"]  # ✅ Ensure collection is Recommendations
doctor_collection = db["Doctors"]  # ✅ Ensure Doctors collection is referenced

<<<<<<< HEAD
db = mongo.db  # Database Reference
users_collection = db.users  # User authentication
screen_test_collection = db.ScreenTest  # ScreenTest answers and risk levels
treatment_collection = db.Recommendations  # Treatment recommendations
doctor_collection = db.Doctors  # Doctor list

# Load trained KNN model, scaler, and encoders
knn_model = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\knn_model.pkl")
scaler = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\scaler.pkl")
specialization_encoder = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\label_encoder_specialization.pkl")
district_encoder = joblib.load(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Isuri_MLModels\label_encoder_district.pkl")

# ------------------- User Authentication -------------------
=======
>>>>>>> 918adbc32473d01b606ca34ac5cc12f81a2f7e49
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
    if not user["password"] == password:
        return jsonify({"error": "Invalid email or password"}), 401

<<<<<<< HEAD
    return jsonify({"message": "Login successful"}), 200


=======
    return jsonify({"message": "Login successful", "username": user["username"]}), 200

@app.route("/treatment")
def treatment_page():
    return render_template("treatment.html")  # Serves treatment.html
>>>>>>> 918adbc32473d01b606ca34ac5cc12f81a2f7e49

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
# @app.route("/get_doctors", methods=["POST"])
# def get_doctors():
#     try:
#         data = request.json
#         specialization = data.get("specialization", "").strip()
#         district = data.get("district", "").strip()

#         # Validate input
#         if not specialization or not district:
#             return jsonify({"error": "Missing specialization or district"}), 400

#         # Use exact field names from MongoDB (fixing space issue)
#         query = {
#             "specialization": {"$regex": f"^{specialization}$", "$options": "i"},
#             "district": {"$regex": f"^{district}$", "$options": "i"}  # Fixed key (removed space)
#         }

#         # Fetch doctors from MongoDB
#         doctors = list(doctor_collection.find(query, {"_id": 0}))

#         if not doctors:
#             return jsonify({"message": "No doctors found"}), 404

#         return jsonify(doctors), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    if users_collection.find_one({"email": data.get("email")}):
        return jsonify({"error": "Email already registered"}), 400

    user_data = {
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "age": data["age"],
        "gender": data["gender"],
        "telephone": data["telephone"],
        "dob": data["dob"],
        "district": data["district"],
        "email": data["email"],
        "password": data["password"],
    }
    users_collection.insert_one(user_data)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/process-image', methods=['POST'])
def process_uploaded_image():
    try:
        file = request.files['image']
        if not file:
            return jsonify({"error": "No file provided"}), 400

        img = PILImage.open(io.BytesIO(file.read()))
        _, depression_level = process_image(img)

        if depression_level == "No face detected. Please upload a clear image with a visible face.":
            return jsonify({"error": depression_level}), 400

        return jsonify({"depression_level": depression_level})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

