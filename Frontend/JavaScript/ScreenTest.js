document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.question');
    const nextButton = document.getElementById('next-btn');
    const resultContainer = document.getElementById('result');
    const form = document.getElementById('riskForm');
    let currentQuestionIndex = 0;

    const answers = {};

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
        for (let answer in answers) {
            totalScore += scores[answers[answer]] || 0;
        }

        return totalScore >= 35 ? "High" : totalScore >= 25 ? "Moderate" : "Low";
    }

    nextButton.addEventListener('click', async function() {
        const selectedRadio = questions[currentQuestionIndex].querySelector('input[type="radio"]:checked');
        if (!selectedRadio) {
            alert('Please select an answer before proceeding.');
            return;
        }

        // Store the answer
        const answer = selectedRadio.value;
        const questionName = selectedRadio.name;
        answers[questionName] = answer;

        if (currentQuestionIndex === 6 || currentQuestionIndex === 8) {
            handleAdditionalQuestions();
        }

        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            showQuestion();
        } else {
            // Send answers to the backend
            await fetch('http://127.0.0.1:5000/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(answers)
            });

            // Calculate risk level
            const riskLevel = calculateRiskLevel();
            resultContainer.innerText = `Risk Level: ${riskLevel}`;
            resultContainer.style.display = 'block';
            form.style.display = 'none';

            // Send risk level to backend
            await fetch('http://127.0.0.1:5000/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(answers)
            });
        }
    });

    showQuestion();
});
