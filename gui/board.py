from tkinter import Canvas
import tkinter as tk
from PIL import Image, ImageTk
from core.game_engine import ChessGame
import os
import chess


class ChessBoard(Canvas):
    # ИСПРАВЛЕНО: Добавлен параметр game в конструктор
    def __init__(self, parent, game, main_window, size=500):
        super().__init__(parent, width=size, height=size)  # создаем холст для доски
        self.pack()

        self.selected_square = None
        self.game = game  # используем переданную игру
        self.main_window = main_window
        self.sq_size = size // 8  # размер одной клетки
        self.piece_images = {}  # словарь для фигурок (ИСПРАВЛЕНО: sq_pict -> piece_images)
        self.possible_moves = []  # Список возможных ходов для выбранной фигуры

        self.bind("<Button-1>", self.on_click)  # какая кнопка мыши будет активна (добавлен обработчик)

        self.load_piece_images()
        self.draw_board()

    def draw_board(self):
        self.delete("all")  # удаляем все что было на доске до этого, после исполнения этого метода

        for r in range(8):
            for c in range(8):
                color = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"  # определяем цвет если четная клетка - белый иначе черный
                x1 = c * self.sq_size
                y1 = r * self.sq_size
                x2 = x1 + self.sq_size
                y2 = y1 + self.sq_size

                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # ИСПРАВЛЕНО: кириллическая 'с' -> латинская 'c'
                convert_coord = chess.square(c, 7 - r)  # создание координаты с учетом разницы в нумерации (в ткинтер y растет вниз)
                piec = self.game.board.piece_at(
                    convert_coord)  # получаем фигуру на клетке текущей (белая пешка - True 1)
                if piec:  # проверяем есть ли фигура на этой клетке (в piec хранится экз. класса chess.piece поэтому так делаем)
                    img_key = self.get_piece_image_key(piec)
                    # ИСПРАВЛЕНО: sq_pict -> piece_images
                    img = self.piece_images.get(img_key)  # получаем значение из словаря с картинками

                    if img:
                        img_x = x1 + (self.sq_size - img.width()) // 2  # вычисляем координаты для центрирования фигуры в клетке
                        img_y = y1 + (self.sq_size - img.height()) // 2

                        self.create_image(  # размещаем фигуру на холсте с тегом для идентификации
                            img_x, img_y, anchor=tk.NW, image=img,
                            tags=f"piece_{convert_coord}"
                        )

        # Подсвечиваем выбранную фигуру (если есть)
        if self.selected_square is not None:
            self.highlight_selected_square()
            self.highlight_possible_moves()

        # Подсвечиваем короля под шахом
        self.highlight_check()

    def get_piece_image_key(self, piec):
        color_prefix = 'w' if piec.color == chess.WHITE else 'b'  # преобразуем True/False в 'w'/'b'
        piec_type = {  # создаем временный словарь, ищем в piec число (тип фигуры) это ключ
            chess.ROOK: 'R',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.QUEEN: 'Q',
            chess.KING: 'K',
            chess.PAWN: 'P'
        }.get(piec.piece_type, '')

        return f"{color_prefix}{piec_type}"  # wP - пример возвращенного зн-я

    def load_piece_images(self):
        pieces = [
            'bB', 'bK', 'bN', 'bP', 'bQ', 'bR',
            'wB', 'wK', 'wN', 'wP', 'wQ', 'wR'
        ]

        piece_size = int(self.sq_size * 0.9)  # Увеличим размер фигур

        for piece_code in pieces:
            current_dir = os.path.dirname(os.path.abspath(__file__))

            img_path = os.path.join(
                current_dir, "assets", "pieces", f"{piece_code}.png"
            )

            if os.path.exists(img_path):
                try:
                    # Загружаем изображение с поддержкой альфа-канала (прозрачности)
                    img = Image.open(img_path).convert("RGBA")

                    # Создаем новое изображение с прозрачным фоном
                    transparent_img = Image.new("RGBA", img.size, (0, 0, 0, 0))

                    # Накладываем фигуру на прозрачный фон
                    transparent_img.paste(img, (0, 0), img)

                    # Масштабируем изображение
                    transparent_img = transparent_img.resize(
                        (piece_size, piece_size),
                        Image.LANCZOS
                    )

                    # Конвертируем для Tkinter
                    self.piece_images[piece_code] = ImageTk.PhotoImage(transparent_img)
                except Exception as e:
                    print(f"Ошибка загрузки {piece_code}.png: {str(e)}")
                    self.piece_images[piece_code] = None
            else:
                print(f"Файл не найден: {img_path}")
                self.piece_images[piece_code] = None

    # визуальное выделение клеток (зеленый цвет) на которые может переместиться выбранная фигура
    def highlight_possible_moves(self):
        for move in self.possible_moves:  # проход по списку возможных ходов

            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)  # для рисование х-7

            x = col * self.sq_size + self.sq_size // 2
            y = row * self.sq_size + self.sq_size // 2

            radius = self.sq_size // 6
            self.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill="green", outline="",
                stipple="gray12",  # Эффект прозрачности
                tags="possible_move"
            )

    def highlight_selected_square(self):  # подсвечиваем выбранную клетку синей рамкой
        col = chess.square_file(self.selected_square)  # получаем координаты выбранной клетки на шахматной доске (0-7)
        row = 7 - chess.square_rank(self.selected_square)

        x1 = col * self.sq_size
        y1 = row * self.sq_size
        x2 = x1 + self.sq_size
        y2 = y1 + self.sq_size

        self.create_rectangle(
            x1, y1, x2, y2,
            outline="blue", width=2,
            tags="selected_square"
        )

    def highlight_check(self):  # подсвечиваем красной рамкой короля, если он под шахом
        if self.game and self.game.board.is_check():
            king_color = self.game.board.turn  # определяем цвет короля, который под шахом
            king_square = self.game.board.king(king_color)  # фигура короля под шахом

            if king_square is not None:
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                x1 = col * self.sq_size
                y1 = row * self.sq_size
                x2 = x1 + self.sq_size
                y2 = y1 + self.sq_size

                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="red", width=3,
                    tags="check_highlight"
                )

    # обработчик кликов
    def on_click(self, event):
        if not self.game or self.game.is_game_over:  # игнорируем клики по доске в случае проигрыша или когда игра не начата
            return

        col = event.x // self.sq_size  # преобразование координат клика мыши в шахматную клетку на доске
        row = event.y // self.sq_size
        square = chess.square(col, 7 - row)  # преобразуем координату для шахматной доски (Y)

        # Если фигура не выбрана - пытаемся выбрать
        if self.selected_square is None:
            if self.try_select_piece(square):
                return
        else:
            # Если кликнули на ту же клетку - снимаем выделение
            if square == self.selected_square:
                self.clear_selection()
                return

            # Пытаемся сделать ход
            self.process_move_attempt(square)

    def try_select_piece(self, square):  # пытаемся выбрать фигуру, возвращаем True при успехе
        piece = self.game.board.piece_at(square)
        if piece and piece.color == self.game.board.turn:  # есть ли фигура на доске и соотв-т ли ее цвет цвету хода игрока
            self.selected_square = square  # запоминаем выбранную клетку

            self.possible_moves = [m for m in self.game.board.legal_moves if
                                   m.from_square == square]  # список возможных ходов (для белой пешки: [Move.from_uci('e2e3'),  Move.from_uci('e2e4')])
            self.draw_board()  # для отображения всех изменений (подсветка ходов легальных)
            return True
        return False

    def process_move_attempt(self, square):  # обрабатываем попытку сделать ход
        from_square = chess.square_name(self.selected_square)
        to_square = chess.square_name(square)
        uci_square = f'{from_square}{to_square}'  # преобразуем координату в формат uci (н-р, e2e3)

        # обработка превращения пешки
        piece = self.game.board.piece_at(self.selected_square)
        if piece and piece.piece_type == chess.PAWN:  # проверяем что текущая фигура - пешка
            rank = chess.square_rank(square)  # получаем номер горизонтали (0-7) клетки назначения
            if rank in [0, 7]:  # достигла ли пешка границы (0 для белой и 7 для черной)
                uci_square += "q"

        # попытка сделать ход
        if self.try_make_move(uci_square, square):
            self.handle_successful_move()
        else:
            self.clear_selection()

    def try_make_move(self, uci_square, square):  # пытаемся выполнить ход, возвращаем True при успехе
        if self.game.make_move(uci_square):  # делаем ход
            for m in self.possible_moves:
                if m.to_square == square:  # соответствует ли конечная клетка хода (move.to_square) клетке, по которой кликнул пользователь (square)
                    self.main_window.add_move_to_history(m)
                    return True
            return False

    def handle_successful_move(self):  # обрабатываем успешный ход
        self.clear_selection()
        self.draw_board()

        if self.game.is_game_over:
            # Если игра завершена, вызывается self.game.get_game_result(), который возвращает строку с результатом (например, "Мат! Победили Белые" или "Пат! Ничья"), это передаётся в update_status, чтобы отобразить его в интерфейсе
            self.main_window.update_status(self.game.get_game_result())

            # дополнительно проверяем, был ли мат -> вызывается show_play_again(), чтобы показать кнопку "Сыграть ещё раз"
            if self.game.board.is_checkmate():
                self.main_window.show_play_again()
        else:
            # если игра не завершена, определяем, чей сейчас ход (self.game.board.turn)
            # chess.WHITE -> ход белых, chess.BLACK -> ход чёрных
            # формируем строку вида "Ход белых" или "Ход чёрных" и выводим через update_status
            turn = "белых" if self.game.board.turn == chess.WHITE else "чёрных"
            self.main_window.update_status(f"Ход {turn}")

    def clear_selection(self):  # cбрасываем текущий выбор фигуры и обновляем доску
        self.selected_square = None
        self.possible_moves = []
        self.draw_board()