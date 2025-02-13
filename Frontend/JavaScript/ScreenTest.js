const questions = [
    "In the past 4 weeks, did you feel so sad that nothing could cheer you up?",
    "In the past 4 weeks, how often did you feel no hope for the future?",
    "In the past 4 weeks, how often did you feel intense shame or guilt?",
    "In the past 4 weeks, how often did you feel worthless?",
    "Have you ever tried to kill yourself?",
    "Have you gone through any upsetting events recently?",
    "Have things been so bad lately that you have thought about killing yourself?",
    "Do you have a current plan for how you would attempt suicide?",
    "Do you have any friends/family members you can confide in if you have a serious problem?"
];

const options = {
    "All of the time": 4,
    "Most of the time": 3,
    "Some of the time": 2,
    "A little of the time": 1,
    "None of the time": 0,
    "Yes": 10,
    "No": 0
};

const extraQuestions = {
    4: { // Question index 4 (suicide attempt)
        "Once": 5,
        "Twice": 10,
        "3+": 15
    },
    8: { // Question index 8 (contact frequency)
        "Daily": 2,
        "A few days a week": 4,
        "Weekly": 6,
        "Monthly": 8,
        "Less than a month": 10
    }
};

const container = document.getElementById("questions-container");

questions.forEach((question, index) => {
    const div = document.createElement("div");
    div.classList.add("question");

    const questionText = document.createElement("p");
    questionText.textContent = question;
    div.appendChild(questionText);

    let optionsSet = options;

    if (extraQuestions[index]) {
        optionsSet = { ...optionsSet, ...extraQuestions[index] };
    }

    Object.keys(optionsSet).forEach(option => {
        const label = document.createElement("label");
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `q${index}`;
        input.value = option;
        label.appendChild(input);
        label.append(option);
        div.appendChild(label);
    });

    container.appendChild(div);
});

document.getElementById("submit-btn").addEventListener("click", () => {
    let score = 0;
    let unanswered = false;

    questions.forEach((_, index) => {
        const selected = document.querySelector(`input[name="q${index}"]:checked`);
        if (!selected) {
            unanswered = true;
        } else {
            score += options[selected.value] || 0;
        }
    });

    if (unanswered) {
        alert("Please answer all questions.");
        return;
    }

    let riskLevel;
    const resultContainer = document.getElementById("result-container");
    const resultText = document.getElementById("risk-result");

    if (score >= 35) {
        riskLevel = "High";
        resultContainer.className = "high";
    } else if (score >= 25) {
        riskLevel = "Moderate";
        resultContainer.className = "moderate";
    } else {
        riskLevel = "Low";
        resultContainer.className = "low";
    }

    resultText.textContent = `Your risk level is: ${riskLevel}`;
    resultContainer.classList.remove("hidden");
});
