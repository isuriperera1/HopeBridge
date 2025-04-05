// document.addEventListener('DOMContentLoaded', function () {
//     const questions = Array.from(document.querySelectorAll('.question'));
//     const resultContainer = document.getElementById('result');
//     const form = document.getElementById('riskForm');
//     let currentQuestionIndex = 0;
//     const answers = {};
//
//     function resetState() {
//         questions.forEach(q => q.style.display = 'none');
//     }
//
//     function showQuestion() {
//         resetState();
//         if (currentQuestionIndex < questions.length) {
//             questions[currentQuestionIndex].style.display = 'block';
//         } else {
//             submitAnswers();
//         }
//     }
//
//     document.querySelectorAll('.answer-option').forEach(option => {
//         option.addEventListener('click', function () {
//             let parent = this.closest('.question');
//             let questionIndex = questions.indexOf(parent);
//             let questionId = parent.id;
//
//             // Save the selected answer
//             answers[questionIndex] = this.dataset.value;
//
//             // Remove 'selected' class from other options and highlight the chosen one
//             parent.querySelectorAll('.answer-option').forEach(opt => opt.classList.remove('selected'));
//             this.classList.add('selected');
//
//             setTimeout(() => {
//                 moveToNextQuestion(questionId, this.dataset.value);
//             }, 300); // Small delay for UI feedback
//         });
//     });
//
//     function moveToNextQuestion(questionId, answer) {
//         if (questionId === "SelectiveQuestion1" && answer === "No") {
//             currentQuestionIndex = findNextQuestionIndex("additionalQuestion1") + 1;
//         } else if (questionId === "SelectiveQuestion2" && answer === "No") {
//             // If "No" is chosen for "Have you ever tried to kill yourself?", skip additionalQuestion1
//             currentQuestionIndex = findNextQuestionIndex("additionalQuestion2") + 1;
//         } else {
//             // Move to the next question normally
//             currentQuestionIndex++;
//         }
//         showQuestion();
//     }
//
//     function findNextQuestionIndex(questionId) {
//         return questions.findIndex(q => q.id === questionId);
//     }
//
//     async function submitAnswers() {
//         try {
//             // Submit answers to backend
//             let response = await fetch('http://127.0.0.1:5000/submit', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify(answers)
//             });
//
//             if (!response.ok) {
//                 throw new Error("Failed to submit answers");
//             }
//
//             // Send answers for risk calculation
//             let riskResponse = await fetch('http://127.0.0.1:5000/calculate', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify(answers)
//             });
//
//             let riskData = await riskResponse.json();
//
//             // Display risk level
//             resultContainer.innerText = `Thank you for completing the test! Your risk level is: ${riskData.risk_level}`;
//             resultContainer.style.display = 'block';
//             form.style.display = 'none';
//         } catch (error) {
//             console.error("Error:", error);
//             resultContainer.innerText = 'An error occurred. Please try again later.';
//             resultContainer.style.display = 'block';
//         }
//     }
//
//     showQuestion();
// });


document.addEventListener('DOMContentLoaded', function () {
    const questions = Array.from(document.querySelectorAll('.question'));
    const resultContainer = document.getElementById('result');
    const form = document.getElementById('riskForm');
    let currentQuestionIndex = 0;
    const answers = {};

    function resetState() {
        questions.forEach(q => q.style.display = 'none');
    }

    function showQuestion() {
        resetState();
        if (currentQuestionIndex < questions.length) {
            questions[currentQuestionIndex].style.display = 'block';
        } else {
            submitAnswers(); // Submit when last question is done
        }
    }

    document.querySelectorAll('.answer-option').forEach(option => {
        option.addEventListener('click', function () {
            let parent = this.closest('.question');
            let questionIndex = questions.indexOf(parent);
            let questionId = parent.id;

            // Save the selected answer
            answers[questionId] = this.dataset.value;

            // Remove 'selected' class from other options and highlight the chosen one
            parent.querySelectorAll('.answer-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');

            setTimeout(() => {
                moveToNextQuestion(questionId, this.dataset.value);
            }, 300); // Small delay for UI feedback
        });
    });

    function moveToNextQuestion(questionId, answer) {
        if (questionId === "SelectiveQuestion1" && answer === "No") {
            currentQuestionIndex = findNextQuestionIndex("additionalQuestion1") + 1;
        } else if (questionId === "SelectiveQuestion2" && answer === "No") {
            currentQuestionIndex = findNextQuestionIndex("additionalQuestion2") + 1;
        } else {
            currentQuestionIndex++;
        }
        showQuestion();
    }

    function findNextQuestionIndex(questionId) {
        return questions.findIndex(q => q.id === questionId);
    }

    async function submitAnswers() {
        try {
            // Submit answers and receive risk level
            let response = await fetch('http://127.0.0.1:5000/submit-screen-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(answers)
            });

            if (!response.ok) {
                throw new Error("Failed to submit answers");
            }

            let data = await response.json();

            // Display risk level
            resultContainer.innerText = `Thank you for completing the test! Your risk level is: ${data.risk_level}`;
            resultContainer.style.display = 'block';
            form.style.display = 'none';
        } catch (error) {
            console.error("Error:", error);
            resultContainer.innerText = 'An error occurred. Please try again later.';
            resultContainer.style.display = 'block';
        }
    }

    showQuestion();
});

