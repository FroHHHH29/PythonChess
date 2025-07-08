import chess


class ChessGame:
    def __init__(self):
        self.board = chess.Board() #создаём стандартную шахматную доску в начальной позиции
        self.resigned = False #флаг сдачи (изначально False)

    def make_move(self, move_uci: str) -> bool:
        try:
            move = chess.Move.from_uci(move_uci) #пытаемся преобразовать строку `move_uci` в объект `chess.Move`
            if move in self.board.legal_moves:
                #является ли этот ход легальным (то есть находится ли он в списке `self.board.legal_moves`).
                #если да, то выполняет ход с помощью `self.board.push(move)`
                self.board.push(move)
                return True

            if len(move_uci) == 4:
                move = chess.Move.from_uci(move_uci + "q")
                if move in self.board.legal_moves:
                    self.board.push(move)
                    return True

            #если ход не был легальным, и при этом длина строки `move_uci` равна 4
            #(то есть это обычный ход без указания превращения, например, "e7e8"), то метод пытается
            #добавить букву 'q' (превращение в ферзя) и снова проверить легальность хода.
            #Это делается для удобства, чтобы не заставлять игрока всегда указывать превращение.
            #если такой ход (с превращением в ферзя) легален, то он выполняется.

            return False
        except ValueError:
            return False

    @property
    def is_game_over(self) -> bool:
        return self.resigned or self.board.is_game_over()
    #`return self.resigned or self.board.is_game_over()` - игра считается законченной, если:
    #- игрок сдался (`self.resigned` установлен в True)
    #- ИЛИ на доске наступила одна из конечных ситуаций (мат, пат и т.д.), что проверяется методом `is_game_over()` из библиотеки `chess`

    def resign(self): #вызывается когда игрок сдается
        self.resigned = True

    def get_game_result(self) -> str:
        if self.board.is_checkmate():
            winner = "чёрные" if self.board.turn == chess.WHITE else "белые"
            return f"Мат! Победили {winner.capitalize()}"
   #когда мат, то тот, кто сейчас должен ходить (чей ход, `self.board.turn`), находится под матом и проигрывает.
   #поэтому победитель - противоположный цвет: если сейчас ход белых (`chess.WHITE`), то они проиграли, значит, победили черные, и наоборот.

        elif self.board.is_stalemate():
            return "Пат! Ничья"
        #пат - это ситуация, когда игрок, чей ход, не может сделать ни одного хода, но король не под шахом. Это ничья.

        elif self.board.is_insufficient_material():
            return "Ничья! Недостаточно материала"
        #ничья, когда на доске недостаточно фигур, чтобы поставить мат
        #(например, король против короля, король против короля и слона и т.п.)

        elif self.board.is_seventyfive_moves():
            return "Ничья! Правило 75 ходов"
        #если в течение 75 ходов не было взятия фигуры и не было хода пешкой, то игра заканчивается вничью.
        elif self.board.is_fivefold_repetition():
            return "Ничья! Пятикратное повторение"
        #если одна и та же позиция повторилась на доске пять раз, то игра заканчивается ничьей.
        return "Игра продолжается"
