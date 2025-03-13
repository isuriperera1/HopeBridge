from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB connection string (replace with your own credentials)
client = MongoClient("mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority")
db = client["HopeBridge"]
answers_collection = db["ScreenTest_answers"]  # Collection to store answers
risk_collection = db["ScreenTest_result"]  # Collection to store calculated risk levels

# Route to handle form submission (answers)
@app.route('/submit', methods=['POST'])
def submit_answers():
    data = request.json
    try:
        answers_collection.insert_one(data)
        return jsonify({"message": "Answers received and saved successfully!"}), 200
    except Exception as e:
        print("Error saving answers:", e)
        return jsonify({"error": "Failed to save answers!"}), 500

# Route to calculate and return risk level
@app.route('/calculate', methods=['POST'])
def calculate_risk():
    data = request.json
    scores = {
        "All of the time": 4,
        "Most of the time": 3,
        "Some of the time": 2,
        "A little of the time": 1,
        "None of the time": 0,
        "Yes": 10,
        "No": 0
    }

    total_score = sum(scores.get(answer, 0) for answer in data.values())

    # Determine the risk level
    if total_score >= 35:
        risk_level = "High"
    elif total_score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # Store the risk level in MongoDB
    try:
        risk_collection.insert_one({"risk_level": risk_level, "answers": data})
        print(f"Risk Level '{risk_level}' saved to MongoDB")
    except Exception as e:
        print("Error saving risk level to MongoDB:", e)
        return jsonify({"error": "Failed to save risk level!"}), 500

    return jsonify({"risk_level": risk_level})

if __name__ == '__main__':
    app.run(debug=True)
