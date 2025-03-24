from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, Dict, Any, List, Tuple
import re
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
MONGO_URI = "mongodb+srv://Vinethma:2003Asmi15@cluster0.xrhve.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["HopeBridge"]  # Database name
collection = db["Chatbot"]  # Collection name

# Risk keywords mapped to each question
risk_keywords = {
    "question_1": {
        "no": 0, "never": 0, "fine": 1, "okay": 1, "stable": 1, "normal": 1, "happy": 0, "content": 1, "relaxed": 1, "good": 0,
        "sometimes": 3, "moody": 3, "sad": 4, "low": 3, "tired": 3, "upset": 3, "down": 4, "weak": 5, "gloomy": 4, "stressed": 5,
        "dull": 5, "empty": 6, "blue": 6, "frustrated": 6, "bad": 6, "helpless": 6, "guilt": 7, "useless": 7, "pointless": 7, "crying": 7,
        "miserable": 8, "shaky": 8, "alone": 8, "numb": 8, "afraid": 8, "anxious": 8, "lost": 9, "hopeless": 10, "suffering": 9,
        "tortured": 9, "suicidal": 10, "lifeless": 10, "worthless": 10, "broken": 10, "devastated": 10, "wrecked": 10,
        "burden": 10, "pained": 9, "dreading": 9, "heartbroken": 9, "destroyed": 9, "hurt": 9, "ruined": 9, "regretful": 9, "weakest": 9,
        "shattered": 9, "crushed": 9, "melancholy": 8, "disheartened": 8, "distressed": 8, "lonely": 8, "fatigued": 8, "shaken": 8,
        "trapped": 8, "isolated": 8, "rejected": 8, "excluded": 8, "unwanted": 8, "invisible": 8, "defeated": 8,
        "distraught": 8, "exhausted": 8, "restless": 8, "worn": 7, "insecure": 7, "uneasy": 7, "doomed": 7, "agitated": 7,
        "dejected": 7, "discontent": 7, "resentful": 7, "downhearted": 7, "grieving": 7, "mournful": 7, "pessimistic": 7,
        "dissatisfied": 7, "indifferent": 6, "apathetic": 6, "uncertain": 6, "withdrawn": 6, "demotivated": 6,
        "unmotivated": 6, "unfocused": 6, "drained": 6, "unsettled": 6, "troubled": 6, "worried": 6, "downcast": 6
    },
    "question_2": {
    "no": 0, "yes": 10, "maybe": 5,"joyless": 10, "disinterested": 9, "bored": 8, "unmotivated": 8, "depressed": 8, "indifferent": 7, "apathy": 7, "unfulfilled": 7,
    "disengaged": 6, "dull": 6, "uninspired": 6, "empty": 5, "lacking enthusiasm": 5, "unhappy": 4, "stagnant": 4, "unpleasant": 4, "tired": 4, "loss of interest": 3,
    "unhappy memories": 3, "disheartened": 3,"unengaged": 3, "discontent": 3, "apathetic": 3, "unsatisfied": 3, "resigned": 3, "dissatisfied": 3, "exhausted": 3,
    "uninterested": 3,"frustrated": 4, "lost joy": 5, "distracted": 6, "empty feeling": 6, "overwhelmed": 6, "lack of passion": 6, "disillusioned": 6, "unproductive": 6,
    "neglected": 6, "disconnected": 6, "unresponsive": 6, "disenchanted": 7, "detached": 7, "unattended": 7, "dispirited": 7, "alienated": 7, "unattached": 7, "hopeless": 7,
    "discontented": 7, "withdrawn": 8
    },
    "question_3": {
    "no": 0, "yes": 10, "maybe": 5,
    "insomnia": 10, "restless": 9, "sleepless": 9, "over-sleeping": 8, "disturbed sleep": 8, "waking up early": 8, "trouble falling asleep": 8, "sleep deprivation": 8, "nightmares": 7, "fatigued": 7,
    "sleep disorder": 7, "sleepy": 6, "drowsy": 6, "night sweats": 6, "interrupted sleep": 6, "sleep anxiety": 6, "restlessness": 5, "hypersomnia": 5, "sleep cycle disruption": 5, "exhausted": 5,
    "unsettled sleep": 5, "disturbed routine": 5, "tiredness": 4, "lack of rest": 4, "broken sleep": 4, "fatigue": 4, "troubled sleep": 4, "mood fluctuations": 4, "worn out": 4,
    "distracted": 4, "restful": 4, "irregular sleep": 4, "unproductive sleep": 5, "chaotic sleep": 5, "insomniac": 5, "severe fatigue": 5, "nightmare issues": 5, "tired all day": 5,
    "rushing in sleep": 6, "waking up too early": 6, "sleep issues": 6, "constant tiredness": 6, "disrupted sleep": 6, "sleep loss": 6, "difficult sleep": 6, "abnormal sleep": 6, "broken rest": 6,
    "irregular patterns": 6, "exhaustion": 6, "reduced rest": 6, "hard to sleep": 6, "disturbed patterns": 6, "sleep cycles": 7, "hard to wake up": 7, "struggling to fall asleep": 7,
    "trouble staying asleep": 7, "lack of focus": 7, "late nights": 7, "too much sleep": 7, "too little sleep": 7, "disruptive behavior": 8, "difficulty waking up": 8, "insufficient rest": 8,
    "restless sleep": 8, "trouble relaxing": 8, "poor sleep": 8, "frustrating nights": 8, "unsettled nights": 9, "unproductive": 9, "unrefreshed": 9
    },
    "question_4": {
    "no": 0, "yes": 10, "maybe": 5,
    "stressed": 10, "anxious": 9, "overburdened": 8, "burnout": 8, "pressure": 8, "frustration": 7, "tense": 7, "worry": 7, "panic": 6, "agitated": 6,
    "overworked": 6, "nervous": 6, "stifled": 6, "frantic": 6, "nervous breakdown": 5, "exhausted": 5, "overload": 5, "staggered": 5, "insecure": 5, "fretful": 5,
    "feeling cornered": 5, "tired": 5, "pressure to perform": 4, "overwhelmed": 4, "unsettled": 4, "strained": 4, "too much to handle": 4, "restless": 4, "frustrated": 4,
    "nervous tension": 5, "fearful": 5, "emotional strain": 5, "nervousness": 6, "toxic stress": 6, "strained nerves": 6, "tiredness": 6, "overthinking": 6, "tightness": 6,
    "frantic pace": 6, "upset": 6, "unease": 7, "on edge": 7, "strained focus": 7, "emotional exhaustion": 7, "mental fatigue": 7, "unstable": 7, "incomplete tasks": 7, "aggressive": 7,
    "flustered": 7, "irritable": 7, "restless thoughts": 7, "uncertainty": 8, "mind racing": 8, "lack of control": 8, "reduced productivity": 8, "broken focus": 8,
    "upset stomach": 8, "mental breakdown": 8, "constant worry": 8, "constant thinking": 8, "feeling lost": 8, "troubled thoughts": 8, "paranoia": 8, "unsettling thoughts": 9, "high anxiety": 9
    },
    "question_5": {
    "no": 0, "yes": 10, "maybe": 5,
    "isolated": 10, "alone": 10, "withdrawn": 10, "lonely": 9, "excluded": 9, "distanced": 9, "reclusive": 9, "quiet": 9, "socially distant": 9,
    "cut off": 9, "avoiding others": 9, "isolated feelings": 8, "avoiding contact": 8, "not talking": 8, "shut off": 8, "retreating": 8, "social withdrawal": 8,
    "alone often": 8, "feeling abandoned": 8, "disconnected from others": 8, "anti-social": 8, "indifferent to others": 8, "not reaching out": 8, "feeling rejected": 8,
    "reduced interaction": 8, "mentally distant": 8, "choosing solitude": 8, "withdrawing from friends": 8, "avoiding interaction": 7, "lonely thoughts": 7,
    "depressed social life": 7, "cutting off relationships": 7, "feeling invisible": 7, "not engaging": 7, "retreating into myself": 7, "shutting down": 7,
    "silent": 7, "no connection": 7, "distancing myself": 7, "no desire to socialize": 7, "withdrawing emotionally": 7, "self-imposed isolation": 7, "shut off emotionally": 7,
    "no energy for others": 7, "avoiding friends": 7, "feeling lost in crowds": 7, "not reaching out to family": 7, "drifting away from loved ones": 7, "mood swings": 7,
    "avoiding others' calls": 7, "disengaged": 7, "silent treatments": 7, "unreachable": 7, "turning inward": 7
    },
    "question_6": {
    "no": 0, "yes": 10, "maybe": 5,
    "hopeless": 10, "suicidal": 10, "empty": 10, "unwanted": 9, "burdened": 9, "worthless": 9, "broken": 9, "defeated": 9, "isolated": 9,
    "tired of life": 9, "unloved": 9, "miserable": 9, "lost": 8, "helpless": 8, "destroyed": 8, "unimportant": 8, "unappreciated": 8, "numb": 8,
    "heartbroken": 8, "disconnected": 8, "crushed": 8, "abandoned": 8, "shattered": 8, "torn apart": 8, "desperate": 8, "hopeless thoughts": 8,
    "feeling overwhelmed": 8, "feeling trapped": 8, "rejected": 8, "confused": 8, "feeling small": 8, "not worth it": 8, "stuck": 8, "empty inside": 7,
    "no way out": 7, "no purpose": 7, "feeling hopeless": 7, "no escape": 7, "nobody cares": 7, "feeling defeated": 7, "mental exhaustion": 7,
    "no hope": 7, "longing for relief": 7, "dark thoughts": 7, "consumed by despair": 7, "in pain": 7, "no energy to continue": 7, "lost in darkness": 7,
    "wish for peace": 7, "stressed beyond measure": 7, "feeling drained": 7, "out of options": 7, "feeling ignored": 7, "wanting to give up": 7,
    "living in pain": 7, "feeling worthless": 7, "broken inside": 7
    },
    "question_7": {
    "no": 0, "yes": 10, "maybe": 5,
    "tired": 10, "fatigued": 10, "exhausted": 10, "drained": 9, "weary": 9, "weak": 9, "low energy": 9, "lethargic": 9, "burned out": 8,
    "worn out": 8, "drowsy": 8, "heavy eyes": 8, "sluggish": 8, "depleted": 8, "slow": 8, "lazy": 8, "unmotivated": 7, "lack of drive": 7,
    "unfocused": 7, "inactive": 7, "zoned out": 7, "languid": 7, "low stamina": 7, "energyless": 7, "draining thoughts": 7, "tired of life": 7,
    "unproductive": 7, "uninspired": 7, "sapped strength": 7, "stagnant": 7, "fatigued brain": 7, "lack of vitality": 7, "no energy": 7, "unrefreshed": 7,
    "mental exhaustion": 7, "worn down": 7, "burnout": 7, "lethargy": 7, "listless": 7, "drained spirit": 6, "disengaged": 6, "unenthusiastic": 6,
    "unfocused thoughts": 6, "tired body": 6, "weakness": 6, "feeling run down": 6, "feeling sluggish": 6, "tired heart": 6, "dull energy": 6,
    "physically drained": 6, "constantly tired": 6, "burning out": 6, "mentally exhausted": 6, "drained mentally": 6, "deflated": 6, "low on energy": 6,
    "inactive lifestyle": 6, "exhaustion from stress": 6, "out of energy": 6, "too tired to move": 6, "can't keep up": 6, "stuck in bed": 6, "feeling empty": 6
    },
    "question_8": {
    "no": 0, "yes": 10, "maybe": 5,
    "distracted": 10, "scattered thoughts": 10, "mind wandering": 9, "indecisive": 9, "foggy mind": 9, "unfocused": 9, "confused": 9,
    "easily distracted": 8, "lost focus": 8, "lacking clarity": 8, "trouble thinking clearly": 8, "overthinking": 8, "decision fatigue": 8, "hesitant": 8,
    "forgetful": 8, "unsettled mind": 8, "difficulty deciding": 7, "brain fog": 7, "disoriented": 7, "stuck in thoughts": 7, "confusion": 7, "mental block": 7,
    "unfocused thoughts": 7, "unable to concentrate": 7, "poor focus": 7, "uncertain thoughts": 7, "disorganized mind": 7, "disjointed thoughts": 7,
    "inability to focus": 7, "trouble prioritizing": 7, "lack of direction": 7, "mental fatigue": 7, "hesitant decisions": 7, "lost in thought": 7,
    "wandering thoughts": 6, "incoherent thinking": 6, "sluggish thinking": 6, "tired brain": 6, "indecision": 6, "thoughts all over the place": 6, "can't focus": 6,
    "disengaged mind": 6, "can't think straight": 6, "overwhelmed thoughts": 6, "unable to focus": 6, "misplaced focus": 6, "lack of clarity": 6, "fuzzy thinking": 6,
    "mind blanks": 6, "mentally fatigued": 6, "stumbling over decisions": 6, "unable to prioritize": 6, "can't make decisions": 6, "mental exhaustion": 6, "blank mind": 6
    },
    "question_9": {
        "no": 0, "yes": 10, "maybe": 5,
        "loss of appetite": 10, "overeating": 10, "weight gain": 9, "weight loss": 9, "no hunger": 9,
        "lack of appetite": 9, "binge eating": 8,
        "overeating cravings": 8, "snacking more": 8, "emotional eating": 8, "under eating": 8,
        "no interest in food": 8, "constant hunger": 8, "eating less": 8,
        "poor appetite": 7, "sudden weight change": 7, "eating habits changed": 7, "gained weight": 7, "lost weight": 7,
        "overeating stress": 7, "loss of taste": 7,
        "feeling full quickly": 7, "increased appetite": 7, "stomach issues": 7, "food aversion": 7, "cravings": 7,
        "overeating to cope": 7, "digestive changes": 7,
        "eating irregularly": 7, "snacking excessively": 6, "overeating uncontrollably": 6, "increased food intake": 6,
        "food obsession": 6, "eating to fill void": 6,
        "decreased appetite": 6, "decreased food intake": 6, "no appetite for days": 6, "constant hunger pangs": 6,
        "irregular eating patterns": 6, "eating less than usual": 6,
        "weight fluctuation": 6, "skipping meals": 6, "low energy food": 6, "losing interest in food": 6,
        "no motivation to eat": 6, "not eating enough": 6,
        "eating less often": 6, "overeating habit": 6, "not eating properly": 6, "extreme hunger": 6,
        "changed food preferences": 6, "eating unhealthy": 6, "weight gain concerns": 6
    },
    "question_10": {
    "no": 0, "yes": 10, "maybe": 5,
    "guilty": 10, "worthless": 10, "ashamed": 9, "self-loathing": 9, "regretful": 9, "unworthy": 9, "disappointed in self": 9, "useless": 9,
    "undeserving": 8, "inferior": 8, "shameful": 8, "embarrassed": 8, "feeling wrong": 8, "feeling like a burden": 8, "blaming self": 8, "self-blame": 8,
    "feeling inadequate": 8, "unacceptable": 8, "insignificant": 8, "reproachful": 7, "self-critical": 7, "feeling bad": 7,
    "deserving of nothing": 7, "self-pity": 7, "unlovable": 7, "guilt-ridden": 7, "guilt over past": 7, "low self-worth": 7, "inadequate": 7, "feeling invisible": 7,
    "feeling small": 7, "lost value": 7, "feeling ignored": 7, "feeling unnoticed": 7, "beating self up": 7, "no hope for change": 7, "unimportant": 7,
    "burden on others": 7, "unfit": 7, "useless thoughts": 6, "self-doubt": 6, "feeling like a failure": 6, "feeling like nothing": 6, "no one cares": 6,
    "feeling lost": 6, "feeling neglected": 6, "unappreciated": 6, "nobody needs me": 6, "burden of guilt": 6, "guilt for actions": 6, "feeling hopeless": 6,
    "disappointed with self": 6, "feeling unimportant": 6, "lack of self-worth": 6, "feeling helpless": 6, "shameful thoughts": 6,
    "guilt from past actions": 6, "feeling defeated": 6, "beating myself up": 6, "overwhelming guilt": 6, "lacking confidence": 6, "excessive self-criticism": 6
    }
}

class ActionHandleQuestionFlow(Action):
    def name(self) -> Text:
        return "action_handle_question_flow"

    def validate_user_input(self, user_input: Text) -> Tuple[bool, Text]:
        """ Validates user input against various checks. """
        if not user_input.strip():
            return False, "Please enter a response. Your answer cannot be blank."
        if len(user_input.split()) > 100:
            return False, "Your response is too long. Please keep it under 100 words."
        if "?" in user_input:
            return False, "I'm afraid asking questions is out of scope for me. My expertise is in guiding you through these questions and helping you with your responses. Please focus on answering my questions."
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
            dispatcher.utter_message(text="Hi")
            dispatcher.utter_message(text="If you find it difficult to continue, please type 'Exit'.")
            current_question = "question_1"
            dispatcher.utter_message(response="utter_question_1")
            return [SlotSet("current_question", current_question), SlotSet("user_responses", {})]

        # Get user's last message
        user_input = tracker.latest_message.get("text", "")

        # If user types 'exit', store answers and end conversation
        if user_input.lower() == "exit":
            if user_responses:
                final_score, risk_category = self.calculate_risk(user_responses)
                self.store_conversation_data(tracker, user_responses, risk_category)

            dispatcher.utter_message(text="Thank you for talking to me. Take care.")
            return [SlotSet("current_question", None), SlotSet("user_responses", None),
                    SlotSet("conversation_finished", True)]

        # Validate user input (the same validation you had)
        is_valid, error_message = self.validate_user_input(user_input)
        if not is_valid:
            dispatcher.utter_message(error_message)
            return [SlotSet("current_question", current_question)]  # Stay on the same question

        # Store the user's response in the dictionary
        user_responses.append(user_input.lower())

        # Get user's last intent (you may want to handle this or modify based on your requirements)
        last_intent = tracker.latest_message.get("intent", {}).get("name")

        # Move to next question or handle the final risk score
        if current_question in question_order:
            index = question_order.index(current_question)

            # Send positive/negative response before asking the next question
            if "positive" in last_intent:
                dispatcher.utter_message(response=f"utter_response_{index + 1}_positive")
            else:
                dispatcher.utter_message(response=f"utter_response_{index + 1}_negative")

            # Move to next question if available
            if index + 1 < len(question_order):
                next_question = question_order[index + 1]
                dispatcher.utter_message(response=f"utter_{next_question}")
                return [SlotSet("current_question", next_question), SlotSet("user_responses", user_responses)]

        # After last question, calculate the risk score and display recommendations
        final_score, risk_category = self.calculate_risk(user_responses)

        # Store the conversation data
        self.store_conversation_data(tracker, user_responses, risk_category)

        # End conversation
        dispatcher.utter_message(response="utter_goodbye")
        return [SlotSet("current_question", None), SlotSet("user_responses", None),
                SlotSet("conversation_finished", True)]

    def calculate_risk(self, user_responses):
        """Calculate risk based on keywords per question."""
        total_risk_score = 0

        # Loop over each question-response pair by index
        for index, response in enumerate(user_responses):
            question = f"question_{index + 1}"  # Map the index to the question
            if question in risk_keywords:
                # Iterate through each keyword for the current question
                for keyword, risk_value in risk_keywords[question].items():
                    # If the keyword is found in the user's response, add the risk value
                    if keyword.lower() in response.lower():
                        total_risk_score += risk_value

        # Categorize risk based on the total risk score
        if total_risk_score >= 50:
            return total_risk_score, "High"
        elif 25 <= total_risk_score < 50:
            return total_risk_score, "Medium"
        else:
            return total_risk_score, "Low"

    def store_conversation_data(self, tracker: Tracker, user_responses: Dict[Text, Text], risk_category: Text):
        """Store conversation data in MongoDB."""
        user_id = tracker.sender_id
        conversation_data = {
            "user_id": user_id,
            "responses": user_responses,
            "risk_category": risk_category,
            "timestamp": datetime.now().isoformat()
        }
        collection.insert_one(conversation_data)