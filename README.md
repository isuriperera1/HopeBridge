# HopeBridge Introduction
HopeBridge is an AI-driven mental health assessment and recommendation system designed to evaluate depression risk and recommends personalized healthcare support . The system determines risk levels categorized as low, medium and high. The risk is calculates using four different measurements like Face Recognition which analyzes emotional states, MCQ-based Screening Tests, Chatbot Interactions, and optionally Journal Entries—both of which utilize Sentiment Analysis. Based on the final classification, HopeBridge tailors recommendations using a K-Nearest Neighbors (KNN) model, filtering  doctors by district and specialization for appropriate treatment according to their risk level and age 13 and below or higher. For high-risk users , the system recommends the emergency contact hotline along with the other recommendations. Additionally, HopeBridge aims to maintain a medical profile to track users’ mental health status over time, ensuring continuity of care and improved treatment outcomes.
# Group Members
Isuri Perera - Leader <br />
Vinethma Kodithuwakku <br />
Ahamed Jamal Umar <br />
Osal De Alwis 
# Mentors
module leader - Mr.Prasan Yapa <br />
Tutor - Mrs.Sulari Fernando

# Feature Prototype 
Facial Recognition and Screen test - AI analyzes emotional expressions to detect signs of distress, sadness, or anxiety, aiding in early depression risk assessment.A multiple-choice psychological test evaluates stress, anxiety, and depression based on clinically validated models.<br /> 
Journal Entry - Users can log daily thoughts, with Sentiment Analysis detecting mood patterns for long-term emotional tracking. <br /> 
Chat Bot - A 24/7 AI chatbot interacts with users, analyzes language tone, and escalates high-risk cases. <br />
Treatment and Recommendations: AI generates tailored plans based on mental health assessments and Filters doctors by specialization and location.

# program running steps
app.py <br />
chatbot - Chatbot Setup Guide <br />

This guide explains how to set up and run the chatbot after setting Python 3.10.0 as the interpreter for the entire application. <br />

1. Create a Virtual Environment <br />

Navigate to your Rasa project directory and run: <br />

python -m venv venv <br />

2. Activate the Virtual Environment <br />

Windows (cmd/PowerShell): <br />

venv\Scripts\activate <br />

Mac/Linux: <br />

source venv/bin/activate <br />


3. Install Dependencies <br />

Run the following command to install required packages: <br />

pip install -r requirements.txt <br />

4. Start Rasa Servers <br />

Open two terminals, activate the virtual environment in both, and run: <br />

Terminal 1 - Start Rasa Actions Server <br />

rasa run actions <br />

Terminal 2 - Start Rasa Chatbot in Debug Mode <br />

rasa run --enable-api --debug --cors "*" <br />

5. Connect to Frontend <br />

After running the debug command, the chatbot backend will be accessible. The frontend of the chatbot will work as it connects to the running Rasa server. <br />
