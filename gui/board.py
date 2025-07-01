from tkinter import Tk, Canvas
import tkinter as tk
from PIL import Image, ImageTk
from game_engine import ChessGame
import os
import chess



class ChessBoard(Canvas):
    def __init__(self, parent=None, size=500):
        """Инициализация шахматной доски"""
        super().__init__(parent, width=size, height=size, bg="white")  # создаем холст для доски
        self.pack()

        self.game = ChessGame()  # экземпляр класса ChessGame
        self.sq_size = size // 8  # размер одной клетки
        self.sq_pict = {}  # словарь для хранения изображений фигур
        self.selected_square = None  # выбранная клетка (None если нет выбора)
        self.possible_moves = []  # список возможных ходов
        self.bind("<Button-1>", self.on_click)  # привязка левого клика мыши к обработчику

        self.load_piece_images()  # загрузка изображений фигур
        self.draw_board()  # первоначальная отрисовка доски

    def draw_board(self):
        """Отрисовка шахматной доски и фигур"""
        self.delete("all")  # очищаем холст перед перерисовкой

        # Отрисовка клеток доски
        for r in range(8):
            for c in range(8):
                color = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"  # определяем цвет клетки
                x1 = c * self.sq_size
                y1 = r * self.sq_size
                x2 = x1 + self.sq_size
                y2 = y1 + self.sq_size
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Отрисовка фигур
                сonvert_coord = chess.square(c, 7 - r)  # преобразование координат (в tkinter Y растет вниз)
                piec = self.game.board.piece_at(сonvert_coord)  # получаем фигуру на текущей клетке
                if piec:  # если фигура существует
                    img_key = self.get_piece_image_key(piec)
                    img = self.sq_pict.get(img_key)  # получаем изображение фигуры из словаря

                    if img:
                        # Вычисляем координаты для центрирования фигуры в клетке
                        img_x = x1 + (self.sq_size - img.width()) // 2
                        img_y = y1 + (self.sq_size - img.height()) // 2

                        # Размещаем фигуру на холсте с тегом для идентификации
                        self.create_image(
                            img_x, img_y, anchor=tk.NW, image=img,
                            tags=f"piece_{сonvert_coord}"
                        )

        # Подсветка возможных ходов для выбранной фигуры
        if self.selected_square is not None:
            self.highlight_possible_moves()

    def get_piece_image_key(self, piec):
        """Генерация ключа для изображения фигуры"""
        color_prefix = 'w' if piec.color == chess.WHITE else 'b'  # префикс цвета (w - белые, b - черные)
        # Преобразование типа фигуры в символ
        piec_type = {
            chess.ROOK: 'R',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.QUEEN: 'Q',
            chess.KING: 'K',
            chess.PAWN: 'P'
        }.get(piec.piece_type, '')  # получаем символ типа фигуры или пустую строку

        return f"{color_prefix}{piec_type}"  # пример: 'wK' - белый король

    def load_piece_images(self):
        """Загрузка изображений шахматных фигур"""
        pieces = [
            'bB', 'bK', 'bN', 'bP', 'bQ', 'bR',  # черные фигуры
            'wB', 'wK', 'wN', 'wP', 'wQ', 'wR'  # белые фигуры
        ]

        piece_size = int(self.sq_size * 0.7)  # размер изображений (70% от размера клетки)

        for piece_code in pieces:
            # Формируем путь к файлу с изображением
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "assets", "pieces", f"{piece_code}.gif")

            if os.path.exists(image_path):  # если файл существует
                try:
                    # Загружаем и масштабируем изображение
                    img = Image.open(image_path)
                    img = img.resize((piece_size, piece_size), Image.LANCZOS)
                    self.sq_pict[piece_code] = ImageTk.PhotoImage(img)  # сохраняем в словарь
                except Exception as e:
                    self.sq_pict[piece_code] = None  # в случае ошибки сохраняем None
            else:
                self.sq_pict[piece_code] = None  # если файл не найден

    def highlight_possible_moves(self):
        """Подсветка клеток, на которые можно походить"""
        for move in self.possible_moves:  # проход по списку возможных ходов
            col = chess.square_file(move.to_square)  # получаем координаты клетки назначения
            row = 7 - chess.square_rank(move.to_square)
            x = col * self.sq_size + self.sq_size // 2  # координаты центра клетки
            y = row * self.sq_size + self.sq_size // 2

            radius = self.sq_size // 6  # радиус кружка подсветки
            # Создаем полупрозрачный зеленый кружок
            self.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill="green", outline="",
                stipple="gray12",  # эффект полупрозрачности
                tags="possible_move"
            )

    def on_click(self, event):
        """Обработчик кликов мыши по доске"""
        if not self.game or self.game.is_game_over:  # проверяем идет ли игра
            return

        # Получаем координаты клика
        col = event.x // self.sq_size  # столбец от 0 до 7
        row = event.y // self.sq_size  # строка от 0 до 7
        square = chess.square(col, 7 - row)  # преобразуем в шахматные координаты

        # Если фигура уже выбрана - пытаемся сделать ход
        if self.selected_square is not None:
            from_sq = chess.square_name(self.selected_square)  # например "e2"
            to_sq = chess.square_name(square)  # например "e4"
            move_uci = f"{from_sq}{to_sq}"  # получаем строку хода, например "e2e4"

            move_made = False
            possible_moves_copy = list(self.possible_moves)  # создаем копию списка возможных ходов

            for move in possible_moves_copy:
                if move.to_square == square:  # проверяем, есть ли этот ход в списке возможных
                    # Особый случай: превращение пешки
                    piece = self.game.board.piece_at(self.selected_square)
                    if piece and piece.piece_type == chess.PAWN and row in [0, 7]:
                        move_uci += "q"  # добавляем превращение в ферзя

                    # Пытаемся сделать ход
                    if self.game.make_move(move_uci):
                        move_made = True
                        self.draw_board()  # обновляем доску
                        break  # выходим из цикла после успешного хода

            # После попытки хода сбрасываем состояние
            self.selected_square = None
            self.possible_moves = []
            self.draw_board()

            return  # завершаем обработку клика

        # Если фигура не выбрана - выбираем фигуру
        piece = self.game.board.piece_at(square)
        if piece and piece.color == self.game.board.turn:  # проверяем, что фигура принадлежит текущему игроку
            self.selected_square = square
            # Заполняем список возможных ходов для этой фигуры
            self.possible_moves = [
                move for move in self.game.board.legal_moves
                if move.from_square == square
            ]
            self.draw_board()  # перерисовываем доску с подсветкой возможных ходов
        else:
            # Клик на пустую клетку или чужую фигуру - сбрасываем выбор
            self.selected_square = None
            self.possible_moves = []
            self.draw_board()