import random
from models.deepseek_model import query_deepseek

COLORS = ["R", "G", "B", "Y", "W", "O"]  # Red, Green, Blue, Yellow, White, Orange


class MastermindGame:
    def __init__(self, api_key):
        self.api_key = api_key
        self.secret_code = None
        self.attempts = []
        self.current_guess = None

    def start_new_game(self):
        self.secret_code = [random.choice(COLORS) for _ in range(4)]
        self.attempts = []
        self.current_guess = None

    def calculate_feedback(self, guess):
        # Calculate feedback
        correct_pos = sum(1 for i in range(4) if guess[i] == self.secret_code[i])
        correct_colors = (
            sum(min(guess.count(c), self.secret_code.count(c)) for c in set(guess))
            - correct_pos
        )
        return correct_pos, correct_colors

    def run_game(self, updates_queue, stop_event=None):
        if not self.secret_code:
            self.start_new_game()

        # R G B Y as first guess
        first_guess = ["R", "G", "B", "Y"]
        correct_pos, correct_colors = self.calculate_feedback(first_guess)
        self.attempts.append((first_guess, (correct_pos, correct_colors)))

        reasoning = (
            "<think>\nI need to crack this color code. "
            "I'll get feedback on how many colors are correct and in the right position, "
            "and how many colors are correct but in wrong positions. "
            "Let me start with a diverse guess to get maximum information.\n\n"
            "First attempt: <try>R G B Y</try>\n"
            f"<{correct_pos} correct positions, {correct_colors} correct colors>"
        )

        updates_queue.put(
            {
                "type": "game_update",
                "attempt": first_guess,
                "feedback": (correct_pos, correct_colors),
                "message": f"Attempt 1: {' '.join(first_guess)} -> {correct_pos} correct positions, {correct_colors} correct colors",
            }
        )

        force_ended = False
        while True:
            if stop_event and stop_event.is_set():
                updates_queue.put({"type": "stopped"})
                break

            content, answer = query_deepseek(
                [
                    {
                        "role": "user",
                        "content": f"You're playing Mastermind. The secret code is 4 colors among {COLORS} (colors can be repeated). "
                        "Make guesses using <try>COLOR COLOR COLOR COLOR</try>. "
                        "You'll receive feedback as <m correct_position, n correct_colors>. "
                        "Which means there are m exact matches (right color in right position), "
                        "and for the unmatched positions, there are n colors that indeed appear in the secret code but in wrong positions. "
                        "Important rules about feedback calculation:\n"
                        "1. First check exact matches (correct color in correct position)\n"
                        "2. Then for remaining unmatched positions, count colors that appear in both guess and secret code\n"
                        "3. duplicate colors in guess are counted multiple times if they appear in the secret code\n"
                        "4. correct_colors count excludes the exact matches already counted\n\n"
                        "Examples:\n"
                        "- If secret is R R B G and guess is R G Y B: <1 correct position, 2 correct colors>\n"
                        "  * R in first position is exact match (1)\n"
                        "  * B and G appear in wrong positions (2)\n"
                        "  * Second R in secret can't match anything since first R was already matched\n"
                        "- If secret is R R G G and guess is G G R R: <0 correct position, 4 correct colors>\n"
                        "  * No exact matches (0)\n"
                        "  * All colors appear in wrong positions (4)\n\n"
                        "Don't get stuck on one guess or think too much - try to find the secret code through multiple quick guesses. Now let's start.",
                    }
                ],
                self.api_key,
                stop=["</try>"],
                prefix=reasoning,
                updates_queue=updates_queue,
                limit=1000,
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

            # For force ended reasoning
            if content.endswith("<try>"):
                force_ended = True
                continue

            if "<try>" in content[-20:] or force_ended:
                guess_str = (
                    content if force_ended else content[content.index("<try>") + 5 :]
                )
                guess = guess_str.strip().upper().split()[:4]
                force_ended = False
                correct_pos, correct_colors = self.calculate_feedback(guess)

                self.attempts.append((guess, (correct_pos, correct_colors)))

                updates_queue.put(
                    {
                        "type": "game_update",
                        "attempt": guess,
                        "feedback": (correct_pos, correct_colors),
                        "message": f"Attempt {len(self.attempts)}: {' '.join(guess)} -> {correct_pos} correct positions, {correct_colors} correct colors",
                    }
                )
                reasoning += f"</try>\n<{correct_pos} correct positions, {correct_colors} correct colors>\n"

                if correct_pos == 4:
                    updates_queue.put(
                        {
                            "type": "complete",
                            "message": "Code cracked! 🎉",
                            "secret_code": self.secret_code,
                        }
                    )
                    reasoning += "\n<code cracked! Congratulations!>\n"

        return reasoning, answer
