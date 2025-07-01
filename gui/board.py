import tkinter as tk
import chess
import os
from PIL import Image, ImageTk


class ChessBoard(tk.Canvas):
    def __init__(self, parent, game, main_window, size=500):
        super().__init__(parent, width=size, height=size, bg="white")
        self.game = game
        self.main_window = main_window
        self.square_size = size // 8
        self.piece_images = {}
        self.selected_square = None
        self.possible_moves = []
        self.bind("<Button-1>", self.on_click)

        self.load_piece_images()
        self.draw_board()

    def load_piece_images(self):
        piece_mapping = {
            'R': 'rook',
            'N': 'knight',
            'B': 'bishop',
            'Q': 'queen',
            'K': 'king',
            'P': 'pawn'
        }

        pieces = [
            'bB', 'bK', 'bN', 'bP', 'bQ', 'bR',
            'wB', 'wK', 'wN', 'wP', 'wQ', 'wR'
        ]

        piece_size = int(self.square_size * 0.7)

        for piece_code in pieces:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(
                current_dir, "assets", "pieces", f"{piece_code}.gif"
            )

            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img = img.resize((piece_size, piece_size), Image.LANCZOS)
                    self.piece_images[piece_code] = ImageTk.PhotoImage(img)
                except Exception as e:
                    self.piece_images[piece_code] = None
            else:
                self.piece_images[piece_code] = None

    def get_piece_image_key(self, piece):
        color_prefix = 'w' if piece.color == chess.WHITE else 'b'
        piece_type = {
            chess.ROOK: 'R',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.QUEEN: 'Q',
            chess.KING: 'K',
            chess.PAWN: 'P'
        }.get(piece.piece_type, '')
        return f"{color_prefix}{piece_type}"

    def draw_board(self):
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
                        img_key = self.get_piece_image_key(piece)
                        img = self.piece_images.get(img_key)

                        if img:
                            img_x = x1 + (self.square_size - img.width()) // 2
                            img_y = y1 + (self.square_size - img.height()) // 2
                            self.create_image(
                                img_x, img_y, anchor=tk.NW, image=img,
                                tags=f"piece_{square}"
                            )

        if self.selected_square is not None:
            self.highlight_possible_moves()

        self.highlight_check()

    def highlight_possible_moves(self):
        for move in self.possible_moves:
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            x = col * self.square_size + self.square_size // 2
            y = row * self.square_size + self.square_size // 2

            radius = self.square_size // 6
            self.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill="green", outline="",
                stipple="gray12",
                tags="possible_move"
            )

    def highlight_check(self):
        if self.game and self.game.board.is_check():
            king_color = self.game.board.turn
            king_square = self.game.board.king(king_color)

            if king_square is not None:
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="red", width=3,
                    tags="check_highlight"
                )

    def on_click(self, event):
        if not self.game or self.game.is_game_over:
            return

        col = event.x // self.square_size
        row = event.y // self.square_size
        square = chess.square(col, 7 - row)

        if self.selected_square is not None:
            from_square = chess.square_name(self.selected_square)
            to_square = chess.square_name(square)
            move_uci = f"{from_square}{to_square}"

            move_made = False
            possible_moves_copy = list(self.possible_moves)

            for move in possible_moves_copy:
                if move.to_square == square:
                    piece = self.game.board.piece_at(self.selected_square)
                    if piece and piece.piece_type == chess.PAWN:
                        if row in [0, 7]:
                            move_uci += "q"

                    if self.game.make_move(move_uci):
                        move_made = True
                        self.main_window.add_move_to_history(move)
                        break

            if move_made:
                self.selected_square = None
                self.possible_moves = []
                self.draw_board()
                if self.game.is_game_over:
                    self.main_window.update_status(self.game.get_game_result())
                    if self.game.board.is_checkmate():
                        self.main_window.show_play_again()
                else:
                    turn = "белых" if self.game.board.turn == chess.WHITE else "чёрных"
                    self.main_window.update_status(f"Ход {turn}")
            else:
                self.selected_square = None
                self.possible_moves = []
                self.draw_board()
            return

        piece = self.game.board.piece_at(square)
        if piece and piece.color == self.game.board.turn:
            self.selected_square = square
            self.possible_moves = [
                move for move in self.game.board.legal_moves
                if move.from_square == square
            ]
            self.draw_board()
        else:
            self.selected_square = None
            self.possible_moves = []
            self.draw_board()