from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/signup": {"origins": "*"}})

# Fix MongoDB URI Format (Ensure Correct Database Name)
app.config["MONGO_URI"] = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/HopeBridge?retryWrites=true&w=majority"

#  Initialize PyMongo
mongo = PyMongo(app)

# Ensure MongoDB Connection is Established
try:
    mongo.db.list_collection_names()  # Test MongoDB Connection
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Access 'users' Collection
users_collection = mongo.db.users


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


if __name__ == "__main__":
    app.run(debug=True)
