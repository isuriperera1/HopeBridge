from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, Dict, Any, List, Tuple
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Suicide Keywords (Only High-Risk Words, Adjusted Weights)
suicide_keywords = {
    "suicide": 50, "die": 40, "dead": 40, "kill": 45,
    "worthless": 20, "hopeless": 20, "pointless": 20,
    "burden": 15, "pain": 25, "goodbye": 35, "disappear": 25,
    "suffering": 25, "useless": 20
}

class ActionHandleQuestionFlow(Action):
    def name(self) -> Text:
        return "action_handle_question_flow"

    def validate_user_input(self, user_input: Text) -> Tuple[bool, Text]:
        """ Validates user input against various checks. """

        # Check for blank input
        if not user_input.strip():
            return False, "Please enter a response. Your answer cannot be blank."

        # Check word limit (Minimum 5 words, Maximum 30 words)
        words = user_input.strip().split()
        if len(words) < 5:
            return False, "Your response is too short. Please provide at least 5 words."
        if len(words) > 30:
            return False, "Your response is too long. Please keep it under 30 words."

        # Check if user input is a question
        if "?" in user_input:
            return False, "Please answer my questions. You cannot ask questions."

        # Check for nonsensical input (random characters, repeated letters, or gibberish)
        if re.fullmatch(r"[^a-zA-Z0-9\s]{3,}", user_input) or re.fullmatch(r"([a-zA-Z])\1{2,}", user_input):
            return False, "I'm not sure I understand. Please provide a clear response."

        return True, ""

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the current question slot value
        current_question = tracker.get_slot("current_question")
        user_responses = tracker.get_slot("user_responses") or []  # Store user responses

        # Define the question flow order
        question_order = [
            "question_1", "question_2", "question_3",
            "question_4", "question_5", "question_6",
            "question_7", "question_8", "question_9", "question_10"
        ]

        # If conversation hasn't started, send the first question
        if current_question is None:
            dispatcher.utter_message(text="Hi, please answer the below questions.")
            current_question = "question_1"
            dispatcher.utter_message(response="utter_question_1")
            return [SlotSet("current_question", current_question), SlotSet("user_responses", [])]

        # Get user's last message
        user_input = tracker.latest_message.get("text", "")

        # Validate user input
        is_valid, error_message = self.validate_user_input(user_input)
        if not is_valid:
            dispatcher.utter_message(error_message)
            return [SlotSet("current_question", current_question)]  # Stay on the same question

        # Store user's response
        user_responses.append(user_input)

        # Get user's last intent
        last_intent = tracker.latest_message.get("intent", {}).get("name")

        # Handle response based on current question
        if current_question in question_order:
            index = question_order.index(current_question)

            # Determine appropriate response (positive or negative)
            response_key = f"utter_response_{index + 1}_{'positive' if 'positive' in last_intent else 'negative'}"
            dispatcher.utter_message(response=response_key)

            # Move to next question if available
            if index + 1 < len(question_order):
                next_question = question_order[index + 1]
                dispatcher.utter_message(response=f"utter_{next_question}")
                return [SlotSet("current_question", next_question), SlotSet("user_responses", user_responses)]

        # After last question, calculate risk score
        final_score, risk_category = self.calculate_risk(user_responses)

        # Display recommendation based on risk level
        if risk_category == "High Risk 🚨":
            dispatcher.utter_message(text="Your well-being is important. Please seek immediate help from a mental health professional or reach out to a trusted support system. If you're in crisis, contact a helpline immediately, below are the details of National Institute of Mental Health(NIMH):")
            dispatcher.utter_message(text="National Mental Health Helpline: 1926")
            dispatcher.utter_message(text="Telephone: +94 112 578 234 - 7")
            dispatcher.utter_message(text="Day Treatment Centre: +94 112 578 556")
        elif risk_category == "Medium Risk ⚠️":
            dispatcher.utter_message(text="You might be going through a rough time. Consider talking to a close friend, practicing relaxation techniques, or seeking professional guidance if needed.")
            dispatcher.utter_message(text="Here is an organization where you can get counselling services: Courage Compassion Commitment (CCC) Foundation - 1333, +94 112 692 909")
        else:
            dispatcher.utter_message(text="It’s great that you're doing well! Keep maintaining a healthy routine, engage in activities that make you happy, and stay connected with supportive people. 🌿")

        # End conversation
        dispatcher.utter_message(response="utter_goodbye")
        return [SlotSet("current_question", None), SlotSet("user_responses", None), SlotSet("conversation_finished", True)]

    def calculate_risk(self, user_responses):
        """Calculate risk based on sentiment analysis and high-risk keywords."""

        total_sentiment_score = 0
        total_keyword_score = 0

        for response in user_responses:
            # Sentiment Analysis (Negativity Score * 100, then Normalize)
            sentiment_score = sia.polarity_scores(response)["neg"] * 100
            total_sentiment_score += sentiment_score

            # Suicide Keyword Check (Add risk if found)
            for keyword, risk in suicide_keywords.items():
                if keyword in response.lower():
                    total_keyword_score += risk

        # Normalize Sentiment Score (Divide by 5 to reduce its impact)
        final_sentiment_score = total_sentiment_score / 5

        # Final Risk Score (Capped at 85)
        final_risk_score = min(final_sentiment_score + total_keyword_score, 85)

        # Determine Risk Level
        if final_risk_score >= 70:
            risk_level = "High Risk 🚨"
        elif 40 <= final_risk_score < 70:
            risk_level = "Medium Risk ⚠️"
        else:
            risk_level = "Low Risk ✅"

        return final_risk_score, risk_level