import tkinter as tk
import chess
from gui.board import ChessBoard
from core.game_engine import ChessGame

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Шахматы")
        self.configure(bg='white')
        self.geometry("500x550")
        self.game = ChessGame()

        self.create_start_menu()

    def create_start_menu(self):
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, anchor=tk.CENTER)

        new_game_btn = tk.Button(main_frame, text='Новая игра', command=self.start_game)
        new_game_btn.pack(pady=(20, 10))

        quit_btn = tk.Button(main_frame, text='Выход', command=self.quit)
        quit_btn.pack(pady=(0, 20))

    def start_game(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.game = ChessGame()
        self.create_game_interface()
    
    def create_game_interface(self):
        self.chess_board = ChessBoard(self, self.game, size=400)
        self.chess_board.pack(pady=20)

        self.status_frame = tk.Frame(self)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            self.status_frame, textvariable=self.status_var,
            font=('Arial', 12), bg='lightgray', width=30
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_play_again = tk.Button(
            self.status_frame, text='Сыграть еще раз',
            command=self.new_game, state=tk.DISABLED
        )

        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            control_frame, text='Новая игра',
            command=self.new_game
        ).pack(side=tk.LEFT)

        tk.Button(
            control_frame, text='Сдаться',
            command=self.resign
        ).pack(side=tk.LEFT, padx=10)

        self.update_status('Ход белых')
    
    def new_game(self):
        self.game = ChessGame()
        self.chess_board.game = self.game
        self.chess_board.selected_square = None
        self.chess_board.possible_moves = []
        self.chess_board.draw_board()
        self.update_status('Новая игра! Ход белых')
        self.btn_play_again.pack_forget()
    
    def show_play_again_button(self):

        self.btn_play_again.pack(side=tk.RIGHT)
        self.btn_play_again.config(state=tk.NORMAL)
    
    def resign(self):

        if self.game:
            self.game.resign()
            winner = 'Черные' if self.game.board.turn == chess.WHITE else 'Белые'
            self.update_status(f'{winner} победили! Игрок сдался.')
            self.show_play_again_button()
    
    def update_status(self, message=None):
        if message:
            self.status_var.set(message)
        elif self.game:
            if self.game.is_game_over:
                result = self.game.get_game_result()
                self.status_var.set(result)
                self.show_play_again_button()
            else:
                turn = 'белых' if self.game.board.turn == chess.WHITE else 'черных'
                self.status_var.set(f'Ход {turn}')
                