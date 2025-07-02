import tkinter as tk
import chess
import os
from PIL import Image, ImageTk

class ChessBoard(tk.Canvas):
    def __init__(self, parent, game, main_window, size=500):
        super().__init__(parent, width=size, height=size, bg="white")
        self.game = game  # Ссылка на объект игры (логика шахмат)
        self.main_window = main_window  # Ссылка на главное окно
        self.square_size = size // 8  # Размер одной клетки доски
        self.piece_images = {}  # Словарь для хранения изображений фигур
        self.selected_square = None  # Выбранная клетка (None если ничего не выбрано)
        self.possible_moves = []  # Список возможных ходов для выбранной фигуры
        self.bind("<Button-1>", self.on_click)  # Привязка обработчика кликов мыши

        self.load_piece_images()  # Загрузка изображений фигур
        self.draw_board()  # Первоначальная отрисовка доски

    def load_piece_images(self):
        # Сопоставление типов фигур с названиями файлов
        piece_mapping = {
            'R': 'rook',
            'N': 'knight',
            'B': 'bishop',
            'Q': 'queen',
            'K': 'king',
            'P': 'pawn'
        }

        # Список всех возможных фигур (белые и черные)
        pieces = [
            'bB', 'bK', 'bN', 'bP', 'bQ', 'bR',
            'wB', 'wK', 'wN', 'wP', 'wQ', 'wR'
        ]

        piece_size = int(self.square_size * 0.7)  # Размер фигуры (70% от размера клетки)

        for piece_code in pieces:
            # Получаем путь к файлу с изображением фигуры
            current_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(
                current_dir, "assets", "pieces", f"{piece_code}.gif"
            )

            if os.path.exists(img_path):
                try:
                    # Загружаем изображение и изменяем его размер
                    img = Image.open(img_path)
                    img = img.resize((piece_size, piece_size), Image.LANCZOS)
                    self.piece_images[piece_code] = ImageTk.PhotoImage(img)
                except Exception as e:
                    # Если не удалось загрузить изображение, сохраняем None
                    self.piece_images[piece_code] = None
            else:
                self.piece_images[piece_code] = None

    def get_piece_image_key(self, piece):
        # Префикс цвета: 'w' для белых, 'b' для черных
        color_prefix = 'w' if piece.color == chess.WHITE else 'b'
        # Получаем тип фигуры (буквенное обозначение)
        piece_type = {
            chess.ROOK: 'R',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.QUEEN: 'Q',
            chess.KING: 'K',
            chess.PAWN: 'P'
        }.get(piece.piece_type, '')
        # Возвращаем ключ для словаря изображений (например 'wK' для белого короля)
        return f"{color_prefix}{piece_type}"

    def draw_board(self):
        self.delete("all")  # Очищаем холст перед перерисовкой

        # Рисуем клетки доски
        for row in range(8):
            for col in range(8):
                # Координаты углов клетки
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                # Определяем цвет клетки (чередование светлых и темных)
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Если игра активна, рисуем фигуры
                if self.game:
                    # Получаем квадрат на шахматной доске (переводим координаты)
                    square = chess.square(col, 7 - row)
                    piece = self.game.board.piece_at(square)
                    if piece:
                        # Получаем ключ для изображения фигуры
                        img_key = self.get_piece_image_key(piece)
                        img = self.piece_images.get(img_key)

                        if img:
                            # Вычисляем координаты для центрирования фигуры в клетке
                            img_x = x1 + (self.square_size - img.width()) // 2
                            img_y = y1 + (self.square_size - img.height()) // 2
                            # Рисуем изображение фигуры
                            self.create_image(
                                img_x, img_y, anchor=tk.NW, image=img,
                                tags=f"piece_{square}"
                            )

        # Если выбрана фигура, подсвечиваем возможные ходы
        if self.selected_square is not None:
            self.highlight_possible_moves()

        # Подсвечиваем короля, если он под шахом
        self.highlight_check()

    def highlight_possible_moves(self):
        # Для каждого возможного хода рисуем зеленый кружок
        for move in self.possible_moves:
            # Получаем координаты клетки назначения
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            # Центр клетки
            x = col * self.square_size + self.square_size // 2
            y = row * self.square_size + self.square_size // 2

            radius = self.square_size // 6  # Радиус кружка
            self.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill="green", outline="",
                stipple="gray12",  # Полупрозрачный эффект
                tags="possible_move"
            )

    def highlight_check(self):
        # Проверяем, есть ли шах на доске
        if self.game and self.game.board.is_check():
            # Получаем цвет короля, который под шахом
            king_color = self.game.board.turn
            king_square = self.game.board.king(king_color)

            if king_square is not None:
                # Получаем координаты короля
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                # Рисуем красную рамку вокруг клетки с королем
                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="red", width=3,
                    tags="check_highlight"
                )

    def on_click(self, event):
        # Если игра не активна или завершена, игнорируем клик
        if not self.game or self.game.is_game_over:
            return

        # Получаем координаты клетки по клику мыши
        col = event.x // self.square_size
        row = event.y // self.square_size
        square = chess.square(col, 7 - row)  # Переводим в координаты шахматной доски

        # Если уже выбрана фигура (второй клик)
        if self.selected_square is not None:
            # Получаем названия клеток в нотации (например "e2e4")
            from_square = chess.square_name(self.selected_square)
            to_square = chess.square_name(square)
            move_uci = f"{from_square}{to_square}"

            move_made = False  # Флаг, был ли сделан ход
            possible_moves_copy = list(self.possible_moves)

            # Проверяем все возможные ходы для выбранной фигуры
            for move in possible_moves_copy:
                if move.to_square == square:
                    # Проверка на превращение пешки
                    piece = self.game.board.piece_at(self.selected_square)
                    if piece and piece.piece_type == chess.PAWN:
                        if row in [0, 7]:  # Если пешка дошла до последней горизонтали
                            move_uci += "q"  # По умолчанию превращаем в ферзя

                    # Пытаемся сделать ход
                    if self.game.make_move(move_uci):
                        move_made = True
                        # Добавляем ход в историю
                        self.main_window.add_move_to_history(move)
                        break

            if move_made:
                # Сбрасываем выбор и перерисовываем доску
                self.selected_square = None
                self.possible_moves = []
                self.draw_board()
                # Проверяем окончание игры
                if self.game.is_game_over:
                    self.main_window.update_status(self.game.get_game_result())
                    if self.game.board.is_checkmate():
                        self.main_window.show_play_again()  # Предлагаем сыграть снова
                else:
                    # Обновляем статус с чьим ходом
                    turn = "белых" if self.game.board.turn == chess.WHITE else "чёрных"
                    self.main_window.update_status(f"Ход {turn}")
            else:
                # Если ход не был сделан, сбрасываем выбор
                self.selected_square = None
                self.possible_moves = []
                self.draw_board()
            return

        # Первый клик - выбор фигуры
        piece = self.game.board.piece_at(square)
        # Проверяем, что фигура принадлежит текущему игроку
        if piece and piece.color == self.game.board.turn:
            self.selected_square = square
            # Получаем все возможные ходы для этой фигуры
            self.possible_moves = [
                move for move in self.game.board.legal_moves
                if move.from_square == square
            ]
            self.draw_board()
        else:
            # Если кликнули на пустую клетку или чужую фигуру
            self.selected_square = None
            self.possible_moves = []
            self.draw_board()