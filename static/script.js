let mazeElement = document.getElementById('maze');
let thinkingElement = document.getElementById('thinking');
let startButton = document.getElementById('startButton');

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

function updateThinking(text) {
    thinkingElement.innerHTML += text + '<br>';
    thinkingElement.scrollTop = thinkingElement.scrollHeight;
}

function pollUpdates() {
    fetch('/get_update')
        .then(response => response.json())
        .then(data => {
            if (data.type === 'maze_update') {
                const moveMatch = data.message.match(/Move (\w+)/);
                if (moveMatch && data.message.includes('Failed')) {
                    // Show attempted move animation
                    const attemptedPos = calculateAttemptedPosition(data.current_pos, moveMatch[1]);
                    createMazeDisplay(data.maze, data.current_pos, data.exit_pos, attemptedPos);
                    // Reset display after animation
                    setTimeout(() => {
                        createMazeDisplay(data.maze, data.current_pos, data.exit_pos);
                    }, 300);
                } else {
                    createMazeDisplay(data.maze, data.current_pos, data.exit_pos);
                }
                updateThinking(data.message);
                setTimeout(pollUpdates, 500);
            } else if (data.type === 'thinking') {
                updateThinking(data.message);
                setTimeout(pollUpdates, 500);
            } else if (data.type === 'complete') {
                updateThinking('Maze solving complete!');
                startButton.disabled = false;
            } else {
                setTimeout(pollUpdates, 500);
            }
        });
}

startButton.addEventListener('click', () => {
    startButton.disabled = true;
    thinkingElement.innerHTML = '';
    fetch('/start_maze')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                pollUpdates();
            }
        });
});

// Initialize empty maze
createMazeDisplay([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 0, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1]
], [1, 1], [4, 3]); 