document.addEventListener('DOMContentLoaded', function() {
    const question7 = document.querySelector('select[name="q7"]');
    const additionalQuestion1 = document.getElementById('additionalQuestion1');
    const question9 = document.querySelector('select[name="q9"]');
    const additionalQuestion2 = document.getElementById('additionalQuestion2');

    // Show or hide the additional question based on the answer to question 7
    question7.addEventListener('change', function() {
        if (this.value === 'Yes') {
            additionalQuestion1.style.display = 'block';
        } else {
            additionalQuestion1.style.display = 'none';
        }
    });

    // Show or hide the additional question based on the answer to question 9
    question9.addEventListener('change', function() {
        if (this.value === 'Yes') {
            additionalQuestion2.style.display = 'block';
        } else {
            additionalQuestion2.style.display = 'none';
        }
    });

    // Handle form submission
    document.getElementById('riskForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const scores = {
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
        };

        const formData = new FormData(event.target);
        let totalScore = 0;

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

        document.getElementById('result').innerText = `Risk Level: ${riskLevel}`; // Corrected line
    });
});
