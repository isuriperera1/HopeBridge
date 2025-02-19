document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.question');
    const nextButton = document.getElementById('next-btn');
    const resultContainer = document.getElementById('result');
    const form = document.getElementById('riskForm');
    let currentQuestionIndex = 0;

    function resetState() {
        questions.forEach(q => q.style.display = 'none');
    }

    function showQuestion() {
        resetState();
        questions[currentQuestionIndex].style.display = 'block';
    }

    function handleAdditionalQuestions() {
        const q7Answer = document.querySelector('input[name="q7"]:checked');
        const q9Answer = document.querySelector('input[name="q9"]:checked');

        if (q7Answer && q7Answer.value === 'Yes') {
            document.getElementById('additionalQuestion1').style.display = 'block';
        } else {
            document.getElementById('additionalQuestion1').style.display = 'none';
            if (currentQuestionIndex === 6) {
                currentQuestionIndex++; // Skip additional question
            }
        }

        if (q9Answer && q9Answer.value === 'Yes') {
            document.getElementById('additionalQuestion2').style.display = 'block';
        } else {
            document.getElementById('additionalQuestion2').style.display = 'none';
            if (currentQuestionIndex === 8) {
                currentQuestionIndex++; // Skip additional question
            }
        }
    }

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
        const formData = new FormData(form);

        for (let [_, value] of formData.entries()) {
            totalScore += scores[value] || 0;
        }

        return totalScore >= 35 ? "High" : totalScore >= 25 ? "Moderate" : "Low";
    }

    nextButton.addEventListener('click', function() {
        const selectedRadio = questions[currentQuestionIndex].querySelector('input[type="radio"]:checked');
        if (!selectedRadio) {
            alert('Please select an answer before proceeding.');
            return;
        }

        if (currentQuestionIndex === 6 || currentQuestionIndex === 8) {
            handleAdditionalQuestions();
        }

        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            showQuestion();
        } else {
            resultContainer.innerText = `Risk Level: ${calculateRiskLevel()}`;
            resultContainer.style.display = 'block';
            form.style.display = 'none';
        }
    });

    showQuestion();
});
