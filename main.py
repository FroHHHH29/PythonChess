from core.game_engine import ChessGame
from gui.main_window import MainWindow

def mainn():
    game = ChessGame()
    app = MainWindow(game)
    app.chess_board.draw_board()
    app.mainloop()

if __name__ == "__main__":
    mainn()