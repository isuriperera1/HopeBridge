from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"
mongo = PyMongo(app)

users_collection = mongo.db.users  # Access 'users' collection


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

    return jsonify({"message": "Login successful"}), 200


if __name__ == "__main__":
    app.run(debug=True)
