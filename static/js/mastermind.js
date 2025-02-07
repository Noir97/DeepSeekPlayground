let attemptsElement = document.getElementById('attempts');
let thinkingElement = document.getElementById('thinking');
let startButton = document.getElementById('startButton');

function createAttemptDisplay(attempt, feedback) {
    const row = document.createElement('div');
    row.className = 'attempt-row';
    
    // Create pegs for the guess
    attempt.forEach(color => {
        const peg = document.createElement('div');
        peg.className = `peg peg-${color}`;
        row.appendChild(peg);
    });
    
    // Add feedback
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'feedback';
    feedbackDiv.textContent = `${feedback[0]}⚫ ${feedback[1]}⚪`;
    row.appendChild(feedbackDiv);
    
    attemptsElement.appendChild(row);
}

function updateThinking(text, newLine = true) {
    const streamContainer = thinkingElement.querySelector('.thinking-stream');
    const updatesContainer = thinkingElement.querySelector('.game-updates');

    if (newLine) {
        // Game updates go to the right column
        const p = document.createElement('p');
        p.textContent = text;
        updatesContainer.appendChild(p);
        updatesContainer.scrollTop = updatesContainer.scrollHeight;
    } else {
        // Streaming thoughts go to the left column
        let contentContainer = streamContainer.querySelector('.stream-content');
        if (!contentContainer) {
            contentContainer = document.createElement('p');
            contentContainer.className = 'stream-content';
            streamContainer.appendChild(contentContainer);
        }
        contentContainer.textContent += text;
        streamContainer.scrollTop = streamContainer.scrollHeight;
    }
}

function showSecretCode(code) {
    const secretCodeDiv = document.getElementById('secretCode');
    const pegsContainer = secretCodeDiv.querySelector('.code-pegs');
    pegsContainer.innerHTML = '';
    
    code.forEach(color => {
        const peg = document.createElement('div');
        peg.className = `peg peg-${color}`;
        pegsContainer.appendChild(peg);
    });
    
    secretCodeDiv.style.display = 'block';
}

function pollUpdates() {
    fetch('/get_update')
        .then(response => response.json())
        .then(data => {
            if (data.type === 'game_update') {
                createAttemptDisplay(data.attempt, data.feedback);
                updateThinking(data.message);
                setTimeout(pollUpdates, 500);
            } else if (data.type === 'new_thinking') {
                let streamContainer = thinkingElement.querySelector('.thinking-stream');
                if (streamContainer) {
                    let contentContainer = streamContainer.querySelector('.stream-content');
                    if (contentContainer && contentContainer.textContent) {
                        contentContainer.textContent += '\n\n';
                    }
                }
                setTimeout(pollUpdates, 500);
            } else if (data.type === 'thinking') {
                updateThinking(data.message, false);
                setTimeout(pollUpdates, 500);
            } else if (data.type === 'complete') {
                updateThinking(data.message);
                startButton.disabled = false;
            } else {
                setTimeout(pollUpdates, 500);
            }
        });
}

startButton.addEventListener('click', () => {
    startButton.disabled = true;
    thinkingElement.innerHTML = `
        <div class="thinking-stream"></div>
        <div class="game-updates"></div>
    `;
    attemptsElement.innerHTML = '';
    document.getElementById('secretCode').style.display = 'none';
    fetch('/start_mastermind')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                pollUpdates();
            }
        });
});

// Add a new endpoint to get the current secret code
document.getElementById('showAnswerButton').addEventListener('click', () => {
    fetch('/get_mastermind_code')
        .then(response => response.json())
        .then(data => {
            if (data.secret_code) {
                showSecretCode(data.secret_code);
            }
        });
});

// ... rest of the JavaScript code (pollUpdates, event listeners, etc.) ... 