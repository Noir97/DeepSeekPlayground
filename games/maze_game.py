from models.deepseek_model import query_deepseek
import random


class MazeGame:
    def __init__(self, api_key):
        self.api_key = api_key
        self.maze = None
        self.current_pos = [0, 1]  # Fixed start position
        self.exit_pos = [5, 4]  # Fixed exit position
        self.generate_maze()  # Generate maze on initialization

    def generate_maze(self, width=6, height=6):
        """Generate a random maze with fixed start and end positions."""
        # Initialize maze with all walls
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

        # Create paths using random walk
        def carve_path(x, y):
            self.maze[y][x] = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                new_x, new_y = x + dx * 2, y + dy * 2
                if (
                    1 <= new_x < width - 1  # Keep within inner area
                    and 1 <= new_y < height - 1  # Keep within inner area
                    and self.maze[new_y][new_x] == 1
                ):
                    self.maze[y + dy][x + dx] = 0
                    carve_path(new_x, new_y)

        def has_path_to_exit(start, end):
            """Check if there's a path from start to end using DFS."""
            visited = set()

            def dfs(pos):
                if pos == end:
                    return True
                visited.add(tuple(pos))

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_pos = [pos[0] + dy, pos[1] + dx]
                    if (
                        0 <= new_pos[0] < height
                        and 0 <= new_pos[1] < width
                        and self.maze[new_pos[0]][new_pos[1]] == 0
                        and tuple(new_pos) not in visited
                    ):
                        if dfs(new_pos):
                            return True
                return False

            return dfs(start)

        # Keep generating mazes until we have a valid path
        while True:
            # Reset maze
            self.maze = [[1 for _ in range(width)] for _ in range(height)]

            # Ensure perimeter is walls
            for i in range(width):
                self.maze[0][i] = 1  # Top wall
                self.maze[height - 1][i] = 1  # Bottom wall
            for i in range(height):
                self.maze[i][0] = 1  # Left wall
                self.maze[i][width - 1] = 1  # Right wall

            # Set entrance and exit
            self.maze[0][1] = 0  # Entrance
            self.maze[5][4] = 0  # Exit
            self.maze[1][1] = 0  # First corridor
            self.maze[4][4] = 0  # Last corridor

            # Start carving from entrance corridor
            carve_path(1, 1)

            # Add some random paths for variety (only in inner area)
            for _ in range(5):
                y = random.randint(1, height - 2)
                x = random.randint(1, width - 2)
                self.maze[y][x] = 0

            # Check if there's a valid path
            if has_path_to_exit([1, 0], [5, 4]):
                break

    def start_new_game(self):
        self.generate_maze()
        self.current_pos = [0, 1]  # Reset to starting position

    def is_valid_move(self, new_pos):
        if not (
            0 <= new_pos[0] < len(self.maze) and 0 <= new_pos[1] < len(self.maze[0])
        ):
            return False
        return self.maze[new_pos[0]][new_pos[1]] == 0

    def run_game(self, updates_queue, stop_event=None):
        self.start_new_game()

        # manually move downward to start
        self.current_pos = [1, 1]
        reasoning = (
            "<think>\nOkay, so I'm stuck in a maze and I need to find the exit. "
            "The instructions say I can move up, down, left, or right. "
            "Each time I try a direction, I'll get a response: move success, move failed, or exit found. "
            "My goal is to keep trying different directions step by step until I find the exit. "
            "Let me start by visualizing this maze. Since I don't have any map, "
            "I'll have to explore systematically to avoid going in circles. "
            "Maybe using a right-hand rule or left-hand rule? "
            "Or perhaps just trying each direction methodically.\n\n"
            "Let's see.\n\nAlright, first move: <try>down</try>\n"
            f"<move success, now at {str(self.current_pos)}>\n"
        )
        updates_queue.put(
            {
                "type": "maze_update",
                "maze": self.maze,
                "current_pos": self.current_pos,
                "exit_pos": self.exit_pos,
                "message": f"Move down - Success! Now at {str(self.current_pos)}",
            }
        )

        while True:
            if stop_event and stop_event.is_set():
                updates_queue.put({"type": "stopped"})
                break

            content, answer = query_deepseek(
                [
                    {
                        "role": "user",
                        "content": "You're in a Maze, you can move up, down, left, right. "
                        "During your thinking process, try moving in all directions and see if you can find the exit. "
                        "You have to move to explore the maze without knowing the layout. "
                        "Move one step at a time with the command <try>left</try>. "
                        "Each move will be returned with <move success> or <move failed> (hit the wall) "
                        "or <exit found> (reach the exit). Don't stop until you find the exit. "
                        "Now lets start, starting coordinates are [0, 1], and the exit is at [4, 5]. Try directly while you think, and output the sequence of successful moves as an answer.",
                    }
                ],
                self.api_key,
                stop=["</try>"],
                prefix=reasoning,
                updates_queue=updates_queue,
                stop_event=stop_event,
            )

            if stop_event and stop_event.is_set():
                updates_queue.put({"type": "stopped"})
                break

            if answer:
                break

            # Add a newline marker before new content
            updates_queue.put({"type": "new_thinking"})
            reasoning += content

            if "<try>" in content[-15:]:
                move = content[content.index("<try>") + 5 :].strip().lower()
                new_pos = self.current_pos.copy()

                if move == "up":
                    new_pos[0] -= 1
                elif move == "down":
                    new_pos[0] += 1
                elif move == "left":
                    new_pos[1] -= 1
                elif move == "right":
                    new_pos[1] += 1

                reasoning += "</try>"

                # Check if move is valid
                if self.is_valid_move(new_pos):
                    self.current_pos = new_pos
                    updates_queue.put(
                        {
                            "type": "maze_update",
                            "maze": self.maze,
                            "current_pos": self.current_pos,
                            "exit_pos": self.exit_pos,
                            "message": f"Move {move} - Success! Now at {str(self.current_pos)}",
                        }
                    )
                    reasoning += f"\n<move success, now at {str(self.current_pos)}>\n"
                else:
                    updates_queue.put(
                        {
                            "type": "maze_update",
                            "maze": self.maze,
                            "current_pos": self.current_pos,
                            "exit_pos": self.exit_pos,
                            "message": f"Move {move} - Failed! Now at {str(self.current_pos)}",
                        }
                    )
                    reasoning += f"\n<move failed, now at {str(self.current_pos)}>\n"

                if new_pos == self.exit_pos:
                    updates_queue.put({"type": "complete", "message": "Exit found! 🎉"})
                    reasoning += "\n<exit found! Congratulations!>\n"

        return reasoning, answer
