import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import matplotlib.pyplot as plt
from PIL import Image as PILImage


# Function to preprocess the image before prediction
def preprocess_image(image, target_size):
    image = image.resize(target_size)
    image_array = img_to_array(image)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    image_array = np.expand_dims(image_array, axis=-1)
    image_array = np.expand_dims(image_array, axis=0)
    image_array /= 255.0
    return image_array


# Load the pre-trained model
model = load_model('FR_Model.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


# Function to detect depression level based on emotion scores
def detect_depression_level(emotion_scores):
    negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
    positive_emotions = ['Happy', 'Surprise']
    negative_score = sum(emotion_scores[emotion_labels.index(e)] for e in negative_emotions)
    positive_score = sum(emotion_scores[emotion_labels.index(e)] for e in positive_emotions)
    neutral_score = emotion_scores[emotion_labels.index('Neutral')]
    depression_score = (negative_score * 0.6) + (neutral_score * 0.3) - (positive_score * 0.1)
    return "Low" if depression_score < 0.4 else "Moderate" if depression_score < 0.7 else "High"


# Function to process the image, make predictions, and display results
def process_image(image_path):
    image = PILImage.open(image_path).convert('RGB')
    image_array = preprocess_image(image, target_size=(48, 48))
    predictions = model.predict(image_array)[0]

    # Plot emotion scores
    plt.figure(figsize=(10, 6))
    plt.pie(predictions, labels=emotion_labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab10.colors)
    plt.title('Emotion Scores')
    plt.show()

    # Output the depression level
    print(f"Depression Level: {detect_depression_level(predictions)}")


# Function to capture image from the webcam
def capture_image_from_camera():
    # Open the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    ret, frame = cap.read()

    if ret:
        # Save the captured image
        cv2.imwrite('captured_image.jpg', frame)
        cap.release()
        print("Image captured and saved as 'captured_image.jpg'.")
        process_image('captured_image.jpg')
    else:
        print("Error: Could not read frame.")


# Main function to start the image capture and processing
if __name__ == "__main__":
    # Capture image from the camera
    capture_image_from_camera()
