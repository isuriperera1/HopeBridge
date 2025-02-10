from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, Dict, Any, List, Tuple
from rasa_sdk.events import SlotSet
import re

class ActionHandleQuestionFlow(Action):
    def name(self) -> Text:
        return "action_handle_question_flow"

    def validate_user_input(self, user_input: Text) -> Tuple[bool, Text]:
        """ Validates user input against various checks. """

        # Check for blank input
        if not user_input.strip():
            return False, "Please enter a response. Your answer cannot be blank."

        # Check word limit (Minimum 2 words, Maximum 10 words)
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

        # Define the question flow order
        question_order = [
            "question_1", "question_2", "question_3",
            "question_4", "question_5", "question_6",
            "question_7", "question_8", "question_9", "question_10"
        ]

        # If the conversation hasn't started yet, send the custom message first
        if current_question is None:
            dispatcher.utter_message(text="Hi, please answer the below questions.")
            current_question = "question_1"
            dispatcher.utter_message(response="utter_question_1")
            return [SlotSet("current_question", current_question)]

        # Get user's last message
        user_input = tracker.latest_message.get("text", "")

        # Validate user input
        is_valid, error_message = self.validate_user_input(user_input)
        if not is_valid:
            dispatcher.utter_message(error_message)
            return [SlotSet("current_question", current_question)]  # Stay on the same question

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
                return [SlotSet("current_question", next_question)]

        # If last question is answered, end conversation
        dispatcher.utter_message(response="utter_goodbye")
        return [SlotSet("current_question", None)]