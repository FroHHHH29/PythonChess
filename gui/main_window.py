import tkinter as tk
from .board import ChessBoard


class MainWindow(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Шахмaты")
        self.geometry("500x550")
        self.game = game

        # Шахматная доска
        self.chess_board = ChessBoard(self, game, size=400)
        self.chess_board.pack(pady=20)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self, textvariable=self.status_var,
            bg="lightgray", font=("Arial", 12)
        )
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки управления
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            control_frame, text="Новая игра",
            command=self.new_game
        ).pack(side=tk.LEFT)

        tk.Button(
            control_frame, text="Сдаться",
            command=self.resign
        ).pack(side=tk.LEFT, padx=10)

        self.update_status()

    def new_game(self):
        from core.game_engine import ChessGame
        self.game = ChessGame()
        self.chess_board.game = self.game
        self.chess_board.draw_board()
        self.update_status("Новая игра! Ход белых")

    def resign(self):
        if self.game:
            winner = "Чёрные" if self.game.turn == "white" else "Белые"
            self.update_status(f"{winner} победили! Игрок сдался.")
            self.game = None

    def update_status(self, message=None):
        if message:
            self.status_var.set(message)
        elif self.game:
            if self.game.is_game_over:
                self.status_var.set(self.game.get_game_result())
            else:
                turn = "белых" if self.game.turn == "white" else "чёрных"
                self.status_var.set(f"Ход {turn}")