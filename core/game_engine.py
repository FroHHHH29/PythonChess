import chess


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.resigned = False

    def make_move(self, move_uci: str) -> bool:
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True

            if len(move_uci) == 4:
                move = chess.Move.from_uci(move_uci + "q")
                if move in self.board.legal_moves:
                    self.board.push(move)
                    return True

            return False
        except ValueError:
            return False

    @property
    def is_game_over(self) -> bool:
        return self.resigned or self.board.is_game_over()

    def resign(self):
        self.resigned = True

    def get_game_result(self) -> str:
        if self.board.is_checkmate():
            winner = "чёрные" if self.board.turn == chess.WHITE else "белые"
            return f"Мат! Победили {winner.capitalize()}"
        elif self.board.is_stalemate():
            return "Пат! Ничья"
        elif self.board.is_insufficient_material():
            return "Ничья! Недостаточно материала"
        elif self.board.is_seventyfive_moves():
            return "Ничья! Правило 75 ходов"
        elif self.board.is_fivefold_repetition():
            return "Ничья! Пятикратное повторение"
        return "Игра продолжается"