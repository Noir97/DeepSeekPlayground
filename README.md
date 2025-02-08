# 🎮 DeepSeek Game Room

An innovative collection of interactive games where you can watch an AI (powered by DeepSeek) solve puzzles while explaining its thought process in real-time. What makes this unique is the seamless fusion of AI reasoning with game mechanics - all in-game interactions happen through the AI's detailed thought process.

🔗 **Try it out here:**
Deployed on Railway:
[https://deepseekplayground-production.up.railway.app](https://deepseekplayground-production.up.railway.app)

## 🎯 Current Games

### 🎲 Mastermind
Watch as the AI strategically cracks randomly generated color codes while walking you through its deductive reasoning process step-by-step.

**Key Features:**
- 🎨 Random 4-color codes using 6 vibrant colors (Red, Green, Blue, Yellow, White, Orange)
- 🤔 Detailed explanation of AI's thinking process for each guess
- ✨ Visual feedback with colored pegs
- ⚡ Real-time updates of AI's attempts and reasoning

![Mastermind](./figures/mastermind.png)

### 🗺️ Maze Solver
Follow along as the AI navigates through procedurally generated mazes, sharing its pathfinding strategy in real-time.

**Key Features:**
- 🔄 Random 6x6 maze generation with guaranteed solutions
- 👀 Real-time visualization of AI's movement
- 🧭 Transparent exploration strategy and decision making
- ✅ Clear visual feedback for successful/failed moves

![Maze](./figures/maze.png)

## 🚀 Quick Start

1. Clone the repository
```
git clone https://github.com/Noir97/DeepSeekPlayground.git
```

2. Create and activate a virtual environment (recommended)
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Set your DeepSeek API key
```
export DEEPSEEK_API_KEY="your-api-key-here"
```

5. Run the application
```
python app.py
```

## Structure
```
├── app.py # Flask application
├── requirements.txt # Python dependencies
├── runtime.txt # Python version
├── railway.toml # Railway configuration
├── Procfile # Deployment configuration
├── games/
│ ├── mastermind_game.py
│ └── maze_game.py
├── models/
│ └── deepseek_model.py
├── static/
│ ├── js/
│ │ ├── mastermind.js
│ │ └── maze.js
│ └── style.css
└── templates/
├── base.html
├── mastermind.html
└── maze.html
```

## Dependencies
- Flask
- OpenAI Python Client (for DeepSeek API)
- Python 3.8+

## Future Games (Planned)
- Battleship: AI uses search strategy with hit/miss feedback
- Hot/Cold Treasure Hunt: Navigation with temperature-based feedback
- Lock Picking Puzzle: Pattern deduction from partial information

## Contributing
Feel free to open issues or submit pull requests for improvements or bug fixes.

## License
[MIT License](LICENSE)
