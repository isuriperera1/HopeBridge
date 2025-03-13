# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import cv2
# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.image import img_to_array
# from PIL import Image as PILImage
# import io
#
# app = Flask(__name__)
# CORS(app)
#
# model = load_model('../Pre-trained_Models/FR_Model.h5')
# emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#
# def preprocess_image(image, target_size):
#     image = image.resize(target_size)
#     image_array = img_to_array(image)
#     image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
#     image_array = np.expand_dims(image_array, axis=-1)
#     image_array = np.expand_dims(image_array, axis=0)
#     image_array /= 255.0
#     return image_array
#
# def detect_depression_level(emotion_scores):
#     negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
#     positive_emotions = ['Happy', 'Surprise']
#     negative_score = sum(emotion_scores[emotion_labels.index(e)] for e in negative_emotions)
#     positive_score = sum(emotion_scores[emotion_labels.index(e)] for e in positive_emotions)
#     neutral_score = emotion_scores[emotion_labels.index('Neutral')]
#     depression_score = (negative_score * 0.6) + (neutral_score * 0.3) - (positive_score * 0.1)
#     return "Low" if depression_score < 0.4 else "Moderate" if depression_score < 0.7 else "High"
#
# def detect_face(image):
#     image_array = np.array(image.convert('RGB'))
#     gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
#     faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#     return len(faces) > 0
#
# def process_image(image):
#     if not detect_face(image):
#         return None, "No face detected. Please upload a clear image with a visible face."
#     image_array = preprocess_image(image, target_size=(48, 48))
#     predictions = model.predict(image_array)[0]
#     depression_level = detect_depression_level(predictions)
#     return None, depression_level
#
# @app.route('/process-image', methods=['POST'])
# def process_uploaded_image():
#     try:
#         file = request.files['image']
#         if not file:
#             return jsonify({"error": "No file provided"}), 400
#         img = PILImage.open(io.BytesIO(file.read()))
#         _, depression_level = process_image(img)
#         if depression_level == "No face detected. Please upload a clear image with a visible face.":
#             return jsonify({"error": depression_level}), 400
#         return jsonify({"depression_level": depression_level})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
import cv2
from torchvision import transforms
from PIL import Image as PILImage
import io
from transformers import ViTForImageClassification, ViTFeatureExtractor

app = Flask(__name__)
CORS(app)

# Load the pre-trained ViT model and feature extractor
model_name = "google/vit-base-patch16-224"
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
model = ViTForImageClassification.from_pretrained(model_name)

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def detect_face(image):
    image_array = np.array(image.convert('RGB'))
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0


def preprocess_image(image):
    image = image.convert('RGB')
    inputs = feature_extractor(images=image, return_tensors="pt")
    return inputs


def predict_emotion(image):
    inputs = preprocess_image(image)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits.softmax(dim=-1).numpy()[0]
    return scores


def detect_depression_level(emotion_scores):
    negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
    positive_emotions = ['Happy', 'Surprise']
    negative_score = sum(emotion_scores[emotion_labels.index(e)] for e in negative_emotions)
    positive_score = sum(emotion_scores[emotion_labels.index(e)] for e in positive_emotions)
    neutral_score = emotion_scores[emotion_labels.index('Neutral')]
    depression_score = (negative_score * 0.6) + (neutral_score * 0.3) - (positive_score * 0.1)
    return "Low" if depression_score < 0.4 else "Moderate" if depression_score < 0.7 else "High"


@app.route('/process-image', methods=['POST'])
def process_uploaded_image():
    try:
        file = request.files['image']
        if not file:
            return jsonify({"error": "No file provided"}), 400
        img = PILImage.open(io.BytesIO(file.read()))

        if not detect_face(img):
            return jsonify({"error": "No face detected. Please upload a clear image with a visible face."}), 400

        emotion_scores = predict_emotion(img)
        depression_level = detect_depression_level(emotion_scores)

        return jsonify({"depression_level": depression_level})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

