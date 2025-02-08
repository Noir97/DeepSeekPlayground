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

# Add these global variables
current_game_thread = None
stop_event = threading.Event()  # Renamed from stop_game to stop_event


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/mastermind")
def mastermind():
    return render_template("mastermind.html")


@app.route("/start_mastermind")
def start_mastermind():
    global current_game_thread, stop_event
    # Clear any existing game
    if current_game_thread and current_game_thread.is_alive():
        stop_event.set()
        current_game_thread.join(timeout=1)

    # Clear the queue
    while not game_updates.empty():
        game_updates.get()

    stop_event.clear()
    mastermind_game.start_new_game()  # Reset game state

    def game_runner():
        mastermind_game.run_game(game_updates, stop_event=stop_event)

    current_game_thread = threading.Thread(target=game_runner)
    current_game_thread.start()
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
    global current_game_thread, stop_event
    # Clear any existing game
    if current_game_thread and current_game_thread.is_alive():
        stop_event.set()
        current_game_thread.join(timeout=1)

    # Clear the queue
    while not game_updates.empty():
        game_updates.get()

    stop_event.clear()
    maze_game.start_new_game()  # Reset game state

    def game_runner():
        maze_game.run_game(game_updates, stop_event=stop_event)

    current_game_thread = threading.Thread(target=game_runner)
    current_game_thread.start()
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


@app.route("/stop_game")
def stop_game():
    global current_game_thread, stop_event
    if current_game_thread and current_game_thread.is_alive():
        stop_event.set()  # Signal the game to stop
        current_game_thread.join(timeout=1)  # Wait for thread to finish
        stop_event.clear()  # Reset the stop flag
    return jsonify({"status": "stopped"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
