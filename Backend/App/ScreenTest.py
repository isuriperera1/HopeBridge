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
screen_test_collection = db["ScreenTest"]  # Single collection for storing answers and risk levels

# Route to handle form submission and risk level calculation
@app.route('/submit', methods=['POST'])
def submit_answers():
    data = request.json  # Get submitted answers
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
            "screen_answers": data,
            "risk_level": risk_level
        })
        return jsonify({"message": "Answers received and risk level calculated!", "risk_level": risk_level}), 200
    except Exception as e:
        print("Error saving to MongoDB:", e)
        return jsonify({"error": "Failed to save data!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
