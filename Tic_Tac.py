import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import List, Optional, Tuple

# ------------------------------ Game Logic ------------------------------ #
class Board:
    WIN_LINES = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
        (0, 4, 8), (2, 4, 6)               # diags
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.cells: List[str] = [' '] * 9

    def moves(self) -> List[int]:
        return [i for i, v in enumerate(self.cells) if v == ' ']

    def place(self, idx: int, mark: str) -> bool:
        if 0 <= idx < 9 and self.cells[idx] == ' ':
            self.cells[idx] = mark
            return True
        return False

    def winner(self) -> Optional[str]:
        for a, b, c in Board.WIN_LINES:
            if self.cells[a] != ' ' and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a]
        if ' ' not in self.cells:
            return 'Tie'
        return None

    def clone(self) -> "Board":
        b = Board()
        b.cells = self.cells[:]
        return b


class MinimaxAI:
    def __init__(self, ai_mark: str, human_mark: str, difficulty: str = "Hard"):
        self.ai = ai_mark
        self.human = human_mark
        self.set_difficulty(difficulty)

    def set_marks(self, ai_mark: str, human_mark: str):
        self.ai, self.human = ai_mark, human_mark

    def set_difficulty(self, level: str):
        # Depth caps control strength
        self.level = level
        self.depth_cap = {"Easy": 1, "Medium": 3, "Hard": 9}.get(level, 9)
        self.randomize = level == "Easy"

    def best_move(self, board: Board) -> int:
        # Opening randomization for variety on medium
        if self.level == "Medium" and random.random() < 0.15:
            return random.choice(board.moves())

        best_score = -10**9
        best_idx = random.choice(board.moves())
        for idx in board.moves():
            b = board.clone()
            b.place(idx, self.ai)
            score = self._minimax(b, False, -10**9, 10**9, depth=1)
            if score > best_score:
                best_score, best_idx = score, idx
        return best_idx

    def _score_terminal(self, winner: Optional[str], depth: int) -> int:
        if winner == self.ai:
            return 10 - depth
        if winner == self.human:
            return depth - 10
        return 0  # tie

    def _minimax(self, board: Board, maximizing: bool, alpha: int, beta: int, depth: int) -> int:
        w = board.winner()
        if w is not None:
            return self._score_terminal(w, depth)
        if depth >= self.depth_cap:
            # Shallow heuristic: center > corner > edge
            weights = [3, 1, 3,
                       1, 5, 1,
                       3, 1, 3]
            # Prefer states where AI owns high-weight squares
            s = 0
            for i, v in enumerate(board.cells):
                if v == self.ai: s += weights[i]
                elif v == self.human: s -= weights[i]
            return s

        if maximizing:
            value = -10**9
            for idx in board.moves():
                b = board.clone()
                b.place(idx, self.ai)
                value = max(value, self._minimax(b, False, alpha, beta, depth + 1))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = 10**9
            for idx in board.moves():
                b = board.clone()
                b.place(idx, self.human)
                value = min(value, self._minimax(b, True, alpha, beta, depth + 1))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

# ------------------------------ GUI ------------------------------ #
class TicTacToeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tic Tac Toe — AI Edition")
        self.root.geometry("600x720")
        self.root.resizable(False, False)

        self.board = Board()
        self.player_mark = 'X'
        self.ai_mark = 'O'
        self.turn = 'X'
        self.game_over = False
        self.buttons: List[tk.Button] = []
        self.scores = {'X': 0, 'O': 0, 'Tie': 0}

        self.ai = MinimaxAI(self.ai_mark, self.player_mark, difficulty="Hard")

        self._style()
        self._build_header()
        self._build_toolbar()
        self._build_board()
        self._build_footer()
        self._center()

        self._update_status()

    # ----- UI Builders ----- #
    def _style(self):
        self.bg = "#ecf0f1"
        self.primary = "#3498db"
        self.ai_color = "#27ae60"
        self.human_color = "#e74c3c"
        self.win_color = "#f1c40f"
        self.status_bg = "#34495e"
        self.root.configure(bg=self.bg)

    def _build_header(self):
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(fill="x", pady=(10, 6), padx=10)
        tk.Label(frame, text="🎮 Tic Tac Toe — AI Edition",
                 bg="#2c3e50", fg="white", font=("Arial", 22, "bold")).pack(pady=8)

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=self.bg)
        bar.pack(fill="x", padx=10)

        # Difficulty
        tk.Label(bar, text="Difficulty:", bg=self.bg).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.diff_var = tk.StringVar(value="Hard")
        diff = ttk.Combobox(bar, textvariable=self.diff_var, values=["Easy", "Medium", "Hard"], width=10, state="readonly")
        diff.grid(row=0, column=1, padx=(0, 12))
        diff.bind("<<ComboboxSelected>>", self._on_diff_change)

        # Mark select
        tk.Label(bar, text="Your Mark:", bg=self.bg).grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.mark_var = tk.StringVar(value="X")
        mark = ttk.Combobox(bar, textvariable=self.mark_var, values=["X", "O"], width=5, state="readonly")
        mark.grid(row=0, column=3, padx=(0, 12))
        mark.bind("<<ComboboxSelected>>", self._on_mark_change)

        # Controls
        ttk.Button(bar, text="New Game", command=self.new_game).grid(row=0, column=4, padx=4)
        ttk.Button(bar, text="Reset Scores", command=self.reset_scores).grid(row=0, column=5, padx=4)
        ttk.Button(bar, text="Rules", command=self.show_rules).grid(row=0, column=6, padx=4)
        ttk.Button(bar, text="Quit", command=self.root.quit).grid(row=0, column=7, padx=4)

        for i in range(8):
            bar.grid_columnconfigure(i, weight=0)

        # Status
        self.status = tk.Label(self.root, text="", bg=self.status_bg, fg="white", font=("Arial", 12))
        self.status.pack(fill="x", padx=10, pady=(6, 8))

    def _build_board(self):
        board_frame = tk.Frame(self.root, bg=self.bg)
        board_frame.pack(pady=12)

        self.buttons.clear()
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                b = tk.Button(board_frame, text="",
                              width=6, height=3,
                              font=("Arial", 24, "bold"),
                              bg=self.primary, fg="white",
                              activebackground="#2980b9",
                              command=lambda i=idx: self.on_click(i))
                b.grid(row=r, column=c, padx=6, pady=6)
                self.buttons.append(b)

    def _build_footer(self):
        score_frame = tk.Frame(self.root, bg=self.bg)
        score_frame.pack(pady=(6, 12))
        self.score_label = tk.Label(score_frame, text="", bg=self.bg, fg="#2c3e50", font=("Arial", 12))
        self.score_label.pack()
        self._update_score()

    def _center(self):
        self.root.update_idletasks()
        w, h = 600, 720
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ----- Event Handlers ----- #
    def _on_diff_change(self, _evt=None):
        self.ai.set_difficulty(self.diff_var.get())

    def _on_mark_change(self, _evt=None):
        self.player_mark = self.mark_var.get()
        self.ai_mark = 'O' if self.player_mark == 'X' else 'X'
        self.ai.set_marks(self.ai_mark, self.player_mark)
        self.new_game()

    def on_click(self, idx: int):
        if self.game_over or self.turn != self.player_mark:
            return
        if not self.board.place(idx, self.player_mark):
            return
        self._paint()
        if self._check_end():
            return
        self.turn = self.ai_mark
        self._update_status()
        # Small delay for UX
        self.root.after(350, self.ai_turn)

    def ai_turn(self):
        if self.game_over:
            return
        move = self._choose_ai_move()
        self.board.place(move, self.ai_mark)
        self._paint()
        if self._check_end():
            return
        self.turn = self.player_mark
        self._update_status()

    # ----- Helpers ----- #
    def _choose_ai_move(self) -> int:
        # Opening randomness on Easy
        if self.diff_var.get() == "Easy" and random.random() < 0.35:
            return random.choice(self.board.moves())
        # Prefer center early
        if 4 in self.board.moves():
            if self.diff_var.get() != "Hard" and random.random() < 0.25:
                pass
            else:
                return 4
        return self.ai.best_move(self.board)

    def _check_end(self) -> bool:
        w = self.board.winner()
        if w is None:
            return False
        self.game_over = True
        self._highlight_win(w)
        if w == 'Tie':
            self.scores['Tie'] += 1
            messagebox.showinfo("Game Over", "🤝 Tie game.")
        else:
            self.scores[w] += 1
            if w == self.player_mark:
                messagebox.showinfo("Game Over", f"🎉 You ({w}) win!")
            else:
                messagebox.showinfo("Game Over", f"🤖 AI ({w}) wins.")
        self._update_score()
        self._update_status()
        return True

    def _highlight_win(self, winner: str):
        if winner == 'Tie':
            return
        for a, b, c in Board.WIN_LINES:
            cells = self.board.cells
            if cells[a] == cells[b] == cells[c] == winner:
                for i in (a, b, c):
                    self.buttons[i].configure(bg=self.win_color)
                break

    def _paint(self):
        for i, btn in enumerate(self.buttons):
            val = self.board.cells[i]
            if val == 'X':
                btn.configure(text='X', bg=self.human_color if self.player_mark == 'X' else self.ai_color)
            elif val == 'O':
                btn.configure(text='O', bg=self.human_color if self.player_mark == 'O' else self.ai_color)
            else:
                btn.configure(text='', bg=self.primary)

    def _update_status(self):
        if self.game_over:
            self.status.configure(text="Game over. Click New Game to play again.")
            return
        if self.turn == self.player_mark:
            self.status.configure(text=f"🎯 Your turn ({self.player_mark})")
        else:
            self.status.configure(text=f"🤖 AI thinking... ({self.ai_mark})")

    def _update_score(self):
        self.score_label.configure(
            text=f"Score — You({self.player_mark}): {self.scores[self.player_mark]} | "
                 f"AI({self.ai_mark}): {self.scores[self.ai_mark]} | Ties: {self.scores['Tie']}"
        )

    # ----- Public Actions ----- #
    def new_game(self):
        self.board.reset()
        self.game_over = False
        self.turn = 'X'
        self._paint()
        self._update_status()
        # If player chose 'O', AI starts
        if self.player_mark == 'O':
            self.turn = self.ai_mark
            self._update_status()
            self.root.after(400, self.ai_turn)

    def reset_scores(self):
        self.scores = {'X': 0, 'O': 0, 'Tie': 0}
        self._update_score()

    def show_rules(self):
        rules = (
            "🎮 TIC TAC TOE — RULES\n\n"
            "🎯 Objective: Get three in a row.\n\n"
            "You play as the selected mark. Click any empty square to place your mark.\n"
            "The AI plays with Minimax (alpha–beta) and difficulty affects search depth.\n"
            "Winning lines: rows, columns, diagonals.\n"
        )
        messagebox.showinfo("Rules", rules)


def main():
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
