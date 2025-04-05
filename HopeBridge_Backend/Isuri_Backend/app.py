import sys
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from flask_session import Session
from HopeBridge_Backend.Vinethma_Backend.Login import users_collection
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image as PILImage
import io
from transformers import ViTFeatureExtractor, TFAutoModelForImageClassification


# Add parent folder to sys.path to import sibling module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now safely import from sibling directory



app = Flask(__name__)
CORS(app)

# Load the trained KNN model, scaler, and encoders

# Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
#client = MongoClient(MONGO_URI)
#db = client["HopeBridge"] 
#treatment_collection = db["Recommendations"]  
#doctor_collection = db["Doctors"] 
#

# Configure Flask Session
app.config["SECRET_KEY"] = "supersecretkey"  
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to MongoDB Atlas (Updated to HopeBridge > Recommendations)
MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["HopeBridge"]  
treatment_collection = db["Recommendations"]  
doctor_collection = db["Doctors"]  


#db = mongo.db   Database Reference
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

    return jsonify({"message": "Login successful"}), 200


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

# Load Face Recognition Model
fr_model = load_model(r"C:\Users\sanje\OneDrive\Pictures\IIT FIRST YEAR\2 year -2024\2603\HopeBridge\ML Models\Vinethma_MLModels\FR_Model.h5")

# Load ViT Model for Emotion Recognition
model_name = "google/vit-base-patch16-224"
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
vit_model = TFAutoModelForImageClassification.from_pretrained(model_name)

# Emotion Labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load OpenCV Face Detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def preprocess_image_vit(image):
    """Preprocess image for ViT model"""
    image = image.convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="tf")
    return inputs

def detect_depression_level(emotion_scores):
    """Calculate depression level based on emotion predictions"""
    negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
    positive_emotions = ['Happy', 'Surprise']

    negative_score = sum(emotion_scores[emotion_labels.index(e)] for e in negative_emotions)
    positive_score = sum(emotion_scores[emotion_labels.index(e)] for e in positive_emotions)
    neutral_score = emotion_scores[emotion_labels.index('Neutral')]

    depression_score = (negative_score * 0.6) + (neutral_score * 0.3) - (positive_score * 0.1)

    return "Low" if depression_score < 0.4 else "Moderate" if depression_score < 0.7 else "High"

def detect_face(image):
    """Detect if a face is present in the image"""
    image_array = np.array(image.convert('RGB'))
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0

def process_image(image):
    """Process image for emotion detection using ViT"""
    if not detect_face(image):
        return None, "No face detected. Please upload a clear image with a visible face."

    inputs = preprocess_image_vit(image)
    predictions = vit_model(inputs).logits.numpy()[0]

    # Convert logits to probabilities
    emotion_probs = tf.nn.softmax(predictions).numpy()

    depression_level = detect_depression_level(emotion_probs)
    return None, depression_level

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

@app.route('/submit-screen-test', methods=['POST'])
def submit_screen_test():
    try:
        data = request.json  # Get submitted answers
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Debug: Print the received data
        print("Received data:", data)

        # Scoring system
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

        # Store the answers and risk level in MongoDB
        screen_test_collection.insert_one({
            "screen_answers": data,
            "risk_level": risk_level
        })

        return jsonify({"message": "Answers received and risk level calculated!", "risk_level": risk_level}), 200

    except Exception as e:
        print("Error:", e)  # Debugging line
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500
    
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route("/rasa-chat", methods=["POST"])
def rasa_chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Send user message to Rasa
        rasa_response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": user_message})
        rasa_messages = rasa_response.json()

        # Extract Rasa responses
        bot_responses = [message["text"] for message in rasa_messages if "text" in message]

        return jsonify({"bot_responses": bot_responses})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_specializations_by_risk", methods=["GET"])
def get_specializations_by_risk():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Get age
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    age = int(user.get("age", 0))
    age_group = "Below13" if age < 13 else "Above13"

    # Get risk scores
    scores = treatment_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not scores:
        return jsonify({"error": "Risk scores not found"}), 404

    # Force FaceRecognition to "Low" score
    scores["FaceRecognition"] = 1

    # Define scoring logic
    def calculate_final_risk(score_dict):
        weights = {
            "ScreenTest": 0.3,
            "JournalEntries": 0.2,
            "FaceRecognition": 0.3,
            "ChatbotAnalysis": 0.2
        }
        return round(sum(score_dict.get(k, 0) * weights.get(k, 0) for k in weights), 2)

    def get_risk_level(score):
        if score <= 3:
            return "Low Risk"
        elif score <= 6:
            return "Moderate Risk"
        elif score <= 10:
            return "High Risk"
        return "Unknown Risk"

    risk_score = calculate_final_risk(scores)
    risk_level = get_risk_level(risk_score)

    recommendations = {
        "Below13": {
            "Low Risk": [
                "Child Psychologist", "Child Psychology", "Counselor", "Art Therapist"
            ],
            "Moderate Risk": [
                "Child and Adolescent Psychologist", "Child Counselling Psychologist and Therapist",
                "Mental Health Counselor", "Counseling Psychologist"
            ],
            "High Risk": [
                "Child Psychiatrist", "Paediatric Psychiatrist", "Consultant Paediatric Neurologist", "Clinical Psychologist"
            ],
        },
        "Above13": {
            "Low Risk": [
                "Counseling Psychologist", "Counselor", "Art Therapist", "End of life care"
            ],
            "Moderate Risk": [
                "Applied Psychologist", "Behaviour Therapist", "Cognitive Behavioral Therapy", "Psychological Counselling"
            ],
            "High Risk": [
                "Psychiatrist", "Consultant Neurologist", "Clinical Psychologist", "Clinical Neurologist", "Addiction Professional"
            ],
        }
    }

    relevant_specializations = recommendations[age_group].get(risk_level, [])

    return jsonify({
        "user_id": user_id,
        "age": age,
        "age_group": age_group,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "specializations": relevant_specializations
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
