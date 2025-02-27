document.addEventListener("DOMContentLoaded", function () {
    let videoElement = document.getElementById('webcam');
    let canvasElement = document.getElementById('canvas');
    let context = canvasElement.getContext('2d');
    let capturedImageBlob = null;

    let startWebcamButton = document.getElementById('start-webcam');
    let captureButton = document.getElementById('captureButton');

    if (startWebcamButton) {
        startWebcamButton.addEventListener('click', startWebcam);
    } else {
        console.error("Button 'start-webcam' not found in the DOM.");
    }

    if (captureButton) {
        captureButton.addEventListener('click', captureImage);
    } else {
        console.error("Button 'captureButton' not found in the DOM.");
    }

    function startWebcam() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoElement.srcObject = stream;
                videoElement.play();
            })
            .catch(err => {
                console.error('Error accessing webcam:', err);
                alert('Error accessing webcam. Please check your camera settings and try again.');
            });
    }

    function captureImage() {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

        canvasElement.toBlob(blob => {
            capturedImageBlob = blob;
            processImage(blob);
        });
    }

    function processImage(imageBlob) {
        const formData = new FormData();
        formData.append('image', imageBlob);

        fetch('http://localhost:5000/process-image', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to process image, server responded with status ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Emotion Scores:', data.emotion_scores);
            console.log('Depression Level:', data.depression_level);
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the image. Please try again.');
        });
    }

    function displayResults(data) {
        let resultsContainer = document.getElementById('results');
        resultsContainer.innerHTML = `<p><strong>Depression Level:</strong> ${data.depression_level}</p>`;

        let scoresList = '<ul>';
        for (let emotion in data.emotion_scores) {
            scoresList += `<li>${emotion}: ${data.emotion_scores[emotion]}</li>`;
        }
        scoresList += '</ul>';
        resultsContainer.innerHTML += scoresList;
    }
});
