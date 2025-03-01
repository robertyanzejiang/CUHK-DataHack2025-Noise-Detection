// Update current time
function updateTime() {
    fetch('/get_time')
        .then(response => response.json())
        .then(data => {
            document.getElementById('current-time').textContent = data.time;
        });
}

// Get and display location
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        document.getElementById('current-location').textContent = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    const latitude = position.coords.latitude.toFixed(4);
    const longitude = position.coords.longitude.toFixed(4);
    document.getElementById('current-location').textContent = `Latitude: ${latitude}°, Longitude: ${longitude}°`;
}

function showError(error) {
    let errorMessage = "";
    switch(error.code) {
        case error.PERMISSION_DENIED:
            errorMessage = "Location access denied by user.";
            break;
        case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information unavailable.";
            break;
        case error.TIMEOUT:
            errorMessage = "Location request timed out.";
            break;
        case error.UNKNOWN_ERROR:
            errorMessage = "An unknown error occurred.";
            break;
    }
    document.getElementById('current-location').textContent = errorMessage;
}

// Noise detection functionality
let mediaRecorder;
let audioContext;
let analyser;
let recording = false;
let remainingTime = 10; // 10 seconds recording duration

function startNoiseDetection() {
    if (!recording) {
        navigator.mediaDevices.getUserMedia({ audio: true, video: false })
            .then(stream => {
                recording = true;
                remainingTime = 10;
                document.getElementById('start-recording').textContent = 'Stop Recording';
                document.getElementById('db-value').innerHTML = 'Recording in progress...<br>Time remaining: 10 seconds';

                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                const microphone = audioContext.createMediaStreamSource(stream);
                microphone.connect(analyser);
                analyser.fftSize = 1024;

                const updateTimer = setInterval(() => {
                    remainingTime--;
                    if (remainingTime >= 0) {
                        document.getElementById('db-value').innerHTML = `Recording in progress...<br>Time remaining: ${remainingTime} seconds`;
                    }
                }, 1000);

                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                let maxDecibel = 0;

                const measureNoise = setInterval(() => {
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((acc, value) => acc + value, 0) / dataArray.length;
                    const decibels = Math.round((average / 255) * 100);
                    maxDecibel = Math.max(maxDecibel, decibels);
                    
                    document.getElementById('noise-level').style.width = `${decibels}%`;
                    
                    if (remainingTime <= 0) {
                        clearInterval(measureNoise);
                        clearInterval(updateTimer);
                        recording = false;
                        stream.getTracks().forEach(track => track.stop());
                        document.getElementById('start-recording').textContent = 'Start New Recording';
                        document.getElementById('db-value').innerHTML = `Recording completed<br>Maximum noise level: ${maxDecibel} dB`;
                    }
                }, 100);

            })
            .catch(error => {
                document.getElementById('db-value').textContent = 'Error accessing microphone: ' + error.message;
            });
    } else {
        recording = false;
        remainingTime = 0;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    getLocation();
    setInterval(updateTime, 1000);

    document.getElementById('start-recording').addEventListener('click', startNoiseDetection);

    // Form validation and submission
    const form = document.getElementById('survey-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Get location data
                const locationText = document.getElementById('current-location').textContent;
                let latitude = 0;
                let longitude = 0;
                if (locationText.includes('Latitude')) {
                    const matches = locationText.match(/Latitude: ([\d.-]+)°, Longitude: ([\d.-]+)°/);
                    if (matches) {
                        latitude = matches[1];
                        longitude = matches[2];
                    }
                }

                // Get noise level data
                const dbText = document.getElementById('db-value').textContent;
                let noiseLevel = 0;
                if (dbText.includes('Maximum noise level:')) {
                    const match = dbText.match(/Maximum noise level: (\d+) dB/);
                    if (match) {
                        noiseLevel = match[1];
                    }
                }

                // Create hidden fields for the data
                const addHiddenField = (name, value) => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = name;
                    input.value = value;
                    form.appendChild(input);
                };

                // Add all form data
                addHiddenField('latitude', latitude);
                addHiddenField('longitude', longitude);
                addHiddenField('location_name', document.querySelector('select[name="location-area"]')?.value || '');
                addHiddenField('noise_level', noiseLevel);
                
                // Combine all form data into result
                const formData = new FormData(form);
                const result = {};
                for (let [key, value] of formData.entries()) {
                    if (!['latitude', 'longitude', 'location_name', 'noise_level'].includes(key)) {
                        result[key] = value;
                    }
                }
                addHiddenField('result', JSON.stringify(result));
            }
            form.classList.add('was-validated');
        });
    }
}); 