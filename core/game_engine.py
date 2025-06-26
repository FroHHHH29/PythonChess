import chess

class ChessGame:
    def __init__(self):
        self.board = chess.Board()

    def make_move(self, move_uci: str) -> bool:
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    @property
    def fen(self) -> str:
        return self.board.fen()

    @property
    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    @property
    def turn(self) -> str:
        return "white" if self.board.turn else "black"

    def get_game_result(self) -> str:
        if self.board.is_checkmate():
            return "Мaт! Победили " + ("чёрные" if self.board.turn else "белые")
        elif self.board.is_stalemate():
            return "Пат! Ничья"
        return "Игра продолжается"