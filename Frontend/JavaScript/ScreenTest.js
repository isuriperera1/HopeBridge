document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.question');
    const nextButton = document.getElementById('next-btn');
    const resultContainer = document.getElementById('result');
    let currentQuestionIndex = 0;

    // Hide all questions initially
    function resetState() {
        questions.forEach(question => {
            question.style.display = 'none';
        });
    }

    // Show the current question
    function showQuestion() {
        resetState();
        questions[currentQuestionIndex].style.display = 'block';
    }

    // Show or hide additional questions based on answers
    function handleAdditionalQuestions() {
        const q5Answer = document.querySelector('input[name="q5"]:checked');
        const additionalQuestion1 = document.getElementById('additionalQuestion1');

        if (q5Answer && q5Answer.value === 'Yes') {
            additionalQuestion1.style.display = 'block';
        } else {
            additionalQuestion1.style.display = 'none';
        }
    }

    // Calculate risk level based on answers
    function calculateRiskLevel() {
        const scores = {
            "All of the time": 4,
            "Most of the time": 3,
            "Some of the time": 2,
            "A little of the time": 1,
            "None of the time": 0,
            "Yes": 10,
            "No": 0
        };

        let totalScore = 0;
        const formData = new FormData(document.getElementById('riskForm'));

        for (let [key, value] of formData.entries()) {
            totalScore += scores[value] || 0;
        }

        let riskLevel;
        if (totalScore >= 35) {
            riskLevel = "High";
        } else if (totalScore >= 25) {
            riskLevel = "Moderate";
        } else {
            riskLevel = "Low";
        }

        return riskLevel;
    }

    // Handle next button click
    nextButton.addEventListener('click', function() {
        const selectedRadio = questions[currentQuestionIndex].querySelector('input[type="radio"]:checked');
        if (selectedRadio) {
            if (currentQuestionIndex === 2) { // Assuming question 3 is where q5 is
                handleAdditionalQuestions();
            }
            if (currentQuestionIndex < questions.length - 1) {
                currentQuestionIndex++;
                showQuestion();
            } else {
                const riskLevel = calculateRiskLevel();
                resultContainer.innerText = `Risk Level: ${riskLevel}`;
                resultContainer.style.display = 'block';
                document.getElementById('riskForm').style.display = 'none'; // Hide the form
            }
        } else {
            alert('Please select an answer before proceeding.');
        }
    });

    // Show the first question
    showQuestion();
});
