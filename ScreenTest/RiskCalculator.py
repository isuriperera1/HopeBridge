class RiskCalculator:
    def __init__(self):
        self.scores = {
            "All of the time": 4,
            "Most of the time": 3,
            "Some of the time": 2,
            "A little of the time": 1,
            "None of the time": 0,

            "Yes": 10,
            "No": 0,

            "Once": 5,
            "Twice": 10,
            "3+": 15,

            "Daily": 2,
            "A few days a week": 4,
            "Weekly": 6,
            "Monthly": 8,
            "A less than a month": 10
        }

        self.questions = [
            "1. In the past 4 weeks, did you feel so sad that nothing could cheer you up?",
            "2. In the past 4 weeks, how often did you feel no hope for the future?",
            "3. In the past 4 weeks, how often did you feel intense shame or guilt?",
            "4. In the past 4 weeks, how often did you feel worthless?",
            "5. Have you ever tried to kill yourself? (Yes/No)",
            "6. Have you gone through any upsetting events recently? (Yes/No)",
            "7. Have things been so bad lately that you have thought about killing yourself? (Yes/No)",
            "8. Do you have a current plan for how you would attempt suicide? (Yes/No)",
            "9. Do you have any friends/family members you can confide in if you have a serious problem? (Yes/No)"
        ]

    def ask_questions(self):
        answers = []
        print("Please answer the following questions:")

        for i, question in enumerate(self.questions):
            while True:
                print(question)
                answer = input("Your answer: ").strip()
                if answer in self.scores:
                    answers.append(answer)
                    break
                else:
                    print("Invalid response. Please try again.")

            if i == 4 and answer == "Yes":
                while True:
                    print("If yes, how many times? (Once/Twice/3+)")
                    follow_up = input("Your answer: ").strip()
                    if follow_up in self.scores:
                        answers.append(follow_up)
                        break
                    else:
                        print("Invalid response. Please try again.")

            if i == 8 and answer == "Yes":
                answers[8] = "No"
                while True:
                    print("How often are you in contact with this/these person/people? (Daily/A few days a "
                          "week/Weekly/Monthly/less than a month)")
                    follow_up = input("Your answer: ").strip()
                    if follow_up in self.scores:
                        answers.append(follow_up)
                        break
                    else:
                        print("Invalid response. Please try again.")

        return answers

    def calculate_risk(self, answers):
        total_score = sum(self.scores.get(answer, 0) for answer in answers)

        if total_score >= 35:
            return "High"
        elif 25 <= total_score < 35:
            return "Moderate"
        else:
            return "Low"

if __name__ == "__main__":
    calculator = RiskCalculator()
    answers = calculator.ask_questions()
    risk_level = calculator.calculate_risk(answers)
    print(f"Risk Level: {risk_level}")
