let mazeElement = document.getElementById('maze');
let thinkingElement = document.getElementById('thinking');
let startButton = document.getElementById('startButton');
let stopButton = document.getElementById('stopButton');

function createMazeDisplay(maze, currentPos, exitPos, attemptedPos = null) {
    mazeElement.innerHTML = '';
    
    for (let i = 0; i < maze.length; i++) {
        const row = document.createElement('div');
        row.className = 'maze-row';
        
        for (let j = 0; j < maze[i].length; j++) {
            const cell = document.createElement('div');
            cell.className = 'maze-cell';
            
            if (attemptedPos && i === attemptedPos[0] && j === attemptedPos[1]) {
                cell.className += ' attempted';
            } else if (i === currentPos[0] && j === currentPos[1]) {
                cell.className += ' player';
                cell.textContent = 'P';
            } else if (i === exitPos[0] && j === exitPos[1]) {
                cell.className += ' exit';
                cell.textContent = 'E';
            } else if (maze[i][j] === 1) {
                cell.className += ' wall';
            } else {
                cell.className += ' path';
            }
            
            row.appendChild(cell);
        }
        mazeElement.appendChild(row);
    }
}

function calculateAttemptedPosition(currentPos, move) {
    const newPos = [...currentPos];
    switch(move.toLowerCase()) {
        case 'up':
            newPos[0] -= 1;
            break;
        case 'down':
            newPos[0] += 1;
            break;
        case 'left':
            newPos[1] -= 1;
            break;
        case 'right':
            newPos[1] += 1;
            break;
    }
    return newPos;
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

function pollUpdates() {
    fetch('/get_update')
        .then(response => response.json())
        .then(data => {
            if (data.type === 'stopped') {
                startButton.disabled = false;
                stopButton.disabled = true;
                return;
            }
            if (data.type === 'maze_update') {
                const moveMatch = data.message.match(/Move (\w+)/);
                if (moveMatch && data.message.includes('Failed')) {
                    const attemptedPos = calculateAttemptedPosition(data.current_pos, moveMatch[1]);
                    createMazeDisplay(data.maze, data.current_pos, data.exit_pos, attemptedPos);
                    setTimeout(() => {
                        createMazeDisplay(data.maze, data.current_pos, data.exit_pos);
                    }, 300);
                } else {
                    createMazeDisplay(data.maze, data.current_pos, data.exit_pos);
                }
                updateThinking(data.message);
                setTimeout(pollUpdates, 100);
            } else if (data.type === 'new_thinking') {
                let streamContainer = thinkingElement.querySelector('.thinking-stream');
                if (streamContainer) {
                    let contentContainer = streamContainer.querySelector('.stream-content');
                    if (contentContainer && contentContainer.textContent) {
                        contentContainer.textContent += '\n\n';
                    }
                }
                setTimeout(pollUpdates, 100);
            } else if (data.type === 'thinking') {
                updateThinking(data.message, false);
                setTimeout(pollUpdates, 100);
            } else if (data.type === 'complete') {
                updateThinking('Maze solving complete!');
                startButton.disabled = false;
                stopButton.disabled = true;
            } else if (data.type === 'error') {
                console.error('Game error:', data.message);
                updateThinking('Error: ' + data.message);
                startButton.disabled = false;
                stopButton.disabled = true;
            } else {
                setTimeout(pollUpdates, 100);
            }
        })
        .catch(error => {
            console.error('Error polling updates:', error);
            setTimeout(pollUpdates, 100);
        });
}

startButton.addEventListener('click', () => {
    // Disable/enable buttons
    startButton.disabled = true;
    stopButton.disabled = false;
    
    // Clear displays
    thinkingElement.innerHTML = `
        <div class="thinking-stream"></div>
        <div class="game-updates"></div>
    `;
    
    // Reset maze display
    createMazeDisplay([
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 1]
    ], [0, 1], [5, 4]);
    
    // Start new game
    fetch('/start_maze')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                pollUpdates();
            }
        });
});

stopButton.addEventListener('click', () => {
    fetch('/stop_game')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'stopped') {
                startButton.disabled = false;
                stopButton.disabled = true;
                // Clear thinking area
                thinkingElement.innerHTML = `
                    <div class="thinking-stream"></div>
                    <div class="game-updates"></div>
                `;
            }
        });
});

// Initialize empty 6x6 maze with fixed start and exit positions
createMazeDisplay([
    [1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1],
    [1, 1, 0, 0, 0, 1]
], [1, 0], [5, 4]);

// Add a fetch call to get the initial maze state when the page loads
fetch('/get_maze_state')
    .then(response => response.json())
    .then(data => {
        if (data.maze) {
            createMazeDisplay(data.maze, data.current_pos, data.exit_pos);
        }
    }); 