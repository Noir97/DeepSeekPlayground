from flask import Flask, render_template, jsonify
from games.mastermind_game import MastermindGame
from games.maze_game import MazeGame
import os
from dotenv import load_dotenv
import threading
import queue

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError(
        "No API key found. Please set DEEPSEEK_API_KEY environment variable."
    )

# Queue to store game updates
game_updates = queue.Queue()

# Game instances
mastermind_game = MastermindGame(API_KEY)
maze_game = MazeGame(API_KEY)


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/mastermind")
def mastermind():
    return render_template("mastermind.html")


@app.route("/start_mastermind")
def start_mastermind():
    def game_runner():
        mastermind_game.run_game(game_updates)

    thread = threading.Thread(target=game_runner)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/get_update")
def get_update():
    try:
        update = game_updates.get_nowait()
        return jsonify(update)
    except queue.Empty:
        return jsonify({"type": "no_update"})


@app.route("/maze")
def maze():
    return render_template("maze.html")


@app.route("/start_maze")
def start_maze():
    def game_runner():
        maze_game.run_game(game_updates)

    thread = threading.Thread(target=game_runner)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/get_mastermind_code")
def get_mastermind_code():
    if mastermind_game.secret_code:
        return jsonify({"secret_code": mastermind_game.secret_code})
    return jsonify({"secret_code": None})


@app.route("/get_maze_state")
def get_maze_state():
    if maze_game.maze is None:
        maze_game.generate_maze()  # Generate initial maze if none exists
    return jsonify(
        {
            "maze": maze_game.maze,
            "current_pos": maze_game.current_pos,
            "exit_pos": maze_game.exit_pos,
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
