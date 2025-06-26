import tkinter as tk
import chess
import os
from tkinter import PhotoImage


class ChessBoard(tk.Canvas):
    def __init__(self, parent, game, size=400):
        super().__init__(parent, width=size, height=size, bg="white")
        self.game = game
        self.square_size = size // 8
        self.piece_images = self.load_piece_images()
        self.selected_square = None
        self.bind("<Button-1>", self.on_click)

    def load_piece_images(self):

        images = {}
        pieces = {
            'R': 'ладья', 'N': 'конь', 'B': 'слон',
            'Q': 'ферзь', 'K': 'король', 'P': 'пешка'
        }

        colors = {
            'w': ('white', 'black'),
            'b': ('black', 'white')
        }

        for color_code, color_names in colors.items():
            for piece_code, piece_name in pieces.items():
                key = f"{color_code}{piece_code}"
                try:
                    img = PhotoImage(file=f"assets/pieces/{key}.gif")
                except:

                    img = PhotoImage(width=self.square_size, height=self.square_size)
                    img.put(color_names[0], to=(0, 0, self.square_size, self.square_size))

                    self.create_text(
                        self.square_size // 2,
                        self.square_size // 2,
                        text=piece_name[0].upper(),
                        fill=color_names[1],
                        font=("Arial", self.square_size // 2, "bold")
                    )
                images[key] = img
        return images

    def draw_board(self):
        """Отрисовка шахматной доски с фигурами"""
        self.delete("all")

        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                if self.game:
                    square = chess.square(col, 7 - row)
                    piece = self.game.board.piece_at(square)
                    if piece:
                        piece_code = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
                        img = self.piece_images.get(piece_code)
                        if img:
                            self.create_image(
                                x1 + self.square_size // 2,
                                y1 + self.square_size // 2,
                                image=img
                            )

    def on_click(self, event):
        """Обработка кликов по доске"""
        if not self.game or self.game.is_game_over:
            return

        col = event.x // self.square_size
        row = event.y // self.square_size
        square = chess.square(col, 7 - row)

        if self.selected_square is not None:
            move_uci = f"{chess.square_name(self.selected_square)}{chess.square_name(square)}"

            piece = self.game.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN and row in [0, 7]:
                move_uci += "q"

            if self.game.make_move(move_uci):
                self.draw_board()
                self.master.update_status()
            self.selected_square = None
            return

        if self.game.board.piece_at(square) and (
                (self.game.board.turn == chess.WHITE and self.game.board.piece_at(square).color == chess.WHITE) or
                (self.game.board.turn == chess.BLACK and self.game.board.piece_at(square).color == chess.BLACK)
        ):
            self.selected_square = square

            x = col * self.square_size
            y = row * self.square_size
            self.create_rectangle(
                x, y, x + self.square_size, y + self.square_size,
                outline="red", width=2
            )