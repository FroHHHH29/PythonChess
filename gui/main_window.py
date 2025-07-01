import tkinter as tk
import chess
import pickle
import os
from tkinter import messagebox
from gui.board import ChessBoard
from core.game_engine import ChessGame


# Файл для сохранения игры
SAVE_FILE = "chess_save.pkl"


class MainWindow(tk.Tk):
    def __init__(self):
        """Инициализация главного окна приложения"""
        super().__init__()

        # Основные настройки окна
        self.title("Шахматы")
        self.configure(bg='white')
        self.geometry("700x600")  # Ширина x Высота

        # Игровые компоненты
        self.game = ChessGame()  # Создаем экземпляр игрового движка
        self.chess_board = None  # Здесь будет храниться доска
        self.player_color = chess.WHITE  # Цвет фигур игрока по умолчанию
        self.move_history = []  # История ходов
        self.has_saved_game = os.path.exists(SAVE_FILE)  # Проверяем есть ли сохранение

        # Элементы интерфейса
        self.status_var = tk.StringVar()  # Для отображения статуса игры
        self.btn_play_again = None  # Кнопка "Сыграть еще раз"

        # Создаем стартовое меню
        self.create_start_menu()

    def create_start_menu(self):
        """Создает начальное меню с кнопками"""
        # Обновляем статус наличия сохраненной игры
        self.has_saved_game = os.path.exists(SAVE_FILE)

        # Очищаем окно от предыдущих виджетов
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем основной фрейм меню
        frame = tk.Frame(self, bg='white')
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Заголовок игры
        title = tk.Label(
            frame,
            text="Шахматы",
            font=('Arial', 24, 'bold'),
            bg='white'
        )
        title.pack(pady=20)

        # Кнопка запуска новой игры
        new_game_btn = tk.Button(
            frame,
            text='Новая игра',
            command=self.select_color,  # Переход к выбору цвета
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#f0f0f0'
        )
        new_game_btn.pack(pady=10)

        # Кнопка продолжения сохраненной игры (если есть сохранение)
        if self.has_saved_game:
            continue_btn = tk.Button(
                frame,
                text='Продолжить игру',
                command=self.load_saved_game,
                font=('Arial', 14),
                width=20,
                height=2,
                bg='#d0e0d0'
            )
            continue_btn.pack(pady=10)

        # Кнопка выхода из игры
        quit_btn = tk.Button(
            frame,
            text='Выход',
            command=self.quit,  # Закрытие приложения
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#f0d0d0'
        )
        quit_btn.pack(pady=10)

    def select_color(self):
        """Окно выбора цвета фигур"""
        # Очищаем окно
        for widget in self.winfo_children():
            widget.destroy()

        # Создаем фрейм для элементов выбора цвета
        frame = tk.Frame(self, bg='white')
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Заголовок
        label = tk.Label(
            frame,
            text="Выберите цвет фигур",
            font=('Arial', 18),
            bg='white'
        )
        label.pack(pady=20)

        # Кнопка выбора белых фигур
        white_btn = tk.Button(
            frame,
            text="Играть белыми",
            command=lambda: self.start_game(chess.WHITE),  # Передаем цвет
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#f0f0f0'
        )
        white_btn.pack(pady=10)

        # Кнопка выбора черных фигур
        black_btn = tk.Button(
            frame,
            text="Играть черными",
            command=lambda: self.start_game(chess.BLACK),
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#505050',
            fg='white'
        )
        black_btn.pack(pady=10)

        # Кнопка возврата в главное меню
        back_btn = tk.Button(
            frame,
            text="Назад",
            command=self.create_start_menu,
            font=('Arial', 12),
            width=15,
            height=1,
            bg='#e0e0e0'
        )
        back_btn.pack(pady=20)

    def start_game(self, player_color):
        """Начинает игру с выбранным цветом"""
        self.player_color = player_color  # Сохраняем выбранный цвет
        self.move_history = []  # Очищаем историю ходов
        # Очищаем окно и создаем игровой интерфейс
        for widget in self.winfo_children():
            widget.destroy()
        self.create_game_interface()

    def load_saved_game(self):
        """Загружает сохраненную игру из файла"""
        try:
            with open(SAVE_FILE, 'rb') as f:
                save_data = pickle.load(f)  # Загружаем данные
                self.player_color = save_data['player_color']
                self.move_history = save_data['move_history']

                # Восстанавливаем состояние игры
                self.game = ChessGame()
                self.game.board = chess.Board(save_data['fen'])  # Позиция
                self.game.resigned = save_data['resigned']  # Статус сдачи

            # Очищаем и создаем игровой интерфейс
            for widget in self.winfo_children():
                widget.destroy()
            self.create_game_interface()
        except Exception as e:
            # В случае ошибки показываем сообщение и возвращаем в меню
            messagebox.showerror("Ошибка", f"Не удалось загрузить игру: {str(e)}")
            self.has_saved_game = False
            self.create_start_menu()

    def create_game_interface(self):
        """Создает основной игровой интерфейс"""
        # Главный фрейм для доски и истории ходов
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для шахматной доски (левая часть)
        board_frame = tk.Frame(main_frame)
        board_frame.pack(side=tk.LEFT, padx=10)
        self.chess_board = ChessBoard(board_frame, self.game, self, size=500)
        self.chess_board.pack()

        # Фрейм для истории ходов (правая часть)
        history_frame = tk.LabelFrame(main_frame, text="История ходов", font=('Arial', 12))
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        # Текстовое поле для истории ходов с прокруткой
        self.history_text = tk.Text(
            history_frame,
            height=20,
            width=20,
            font=('Courier New', 10),
            state=tk.DISABLED  # Только для чтения
        )
        scrollbar = tk.Scrollbar(history_frame, command=self.history_text.yview)
        self.history_text.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH)

        # Обновляем отображение истории
        self.update_history_display()

        # Панель статуса (нижняя часть)
        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        # Метка для отображения статуса игры
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 12),
            bg='lightgray',
            width=50
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка "Сыграть еще раз" (изначально скрыта)
        self.btn_play_again = tk.Button(
            status_frame,
            text='Сыграть еще раз',
            command=self.new_game,
            state=tk.DISABLED
        )

        # Панель управления (нижняя часть)
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        # Кнопки управления
        tk.Button(
            control_frame,
            text='Новая игра',
            command=self.new_game
        ).pack(side=tk.LEFT)

        tk.Button(
            control_frame,
            text='Сдаться',
            command=self.resign
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            control_frame,
            text='Выход в меню',
            command=self.return_to_menu
        ).pack(side=tk.LEFT, padx=10)

        # Информация о цвете игрока
        color_info = tk.Label(
            control_frame,
            text=f"Ваш цвет: {'белые' if self.player_color == chess.WHITE else 'черные'}",
            font=('Arial', 10),
            padx=10
        )
        color_info.pack(side=tk.RIGHT)

        # Обновляем статус игры
        if self.game.board.turn == chess.WHITE:
            self.update_status('Ход белых')
        else:
            self.update_status('Ход чёрных')

    def add_move_to_history(self, move):
        """Добавляет ход в историю и обновляет отображение"""
        move_str = move.uci()[:4]  # Берем только первые 4 символа (e2e4)

        # Определяем номер пары ходов (1. e4 e5, 2. Nf3 Nc6 и т.д.)
        pair_number = len(self.move_history) // 2 + 1

        if len(self.move_history) % 2 == 0:
            # Ход белых - новая строка с номером
            self.move_history.append(f"{pair_number}. {move_str}")
        else:
            # Ход черных - добавляем к последней строке
            self.move_history[-1] += f" - {move_str}"
            # Добавляем пустую строку для следующей пары ходов
            self.move_history.append("")

        self.update_history_display()

    def update_history_display(self):
        """Обновляет текстовое поле с историей ходов"""
        self.history_text.config(state=tk.NORMAL)  # Включаем редактирование
        self.history_text.delete(1.0, tk.END)  # Очищаем поле

        # Добавляем все ходы из истории
        for move in self.move_history:
            self.history_text.insert(tk.END, move + "\n")

        # Прокручиваем к концу
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)  # Отключаем редактирование

    def return_to_menu(self):
        """Возвращает в главное меню с подтверждением сохранения"""
        response = messagebox.askyesnocancel(
            "Выход в меню",
            "Хотите сохранить текущую игру перед выходом?",
            icon='question'
        )

        if response is None:  # Если нажата "Отмена"
            return

        if response:  # Если "Да" - сохраняем игру
            self.save_game()
        else:  # Если "Нет" - удаляем сохранение
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            # Сбрасываем состояние игры
            self.game = ChessGame()
            self.move_history = []
            self.has_saved_game = False

        # Возвращаемся в главное меню
        self.create_start_menu()

    def save_game(self):
        """Сохраняет текущее состояние игры в файл"""
        save_data = {
            'fen': self.game.board.fen(),  # Текущая позиция
            'player_color': self.player_color,  # Цвет игрока
            'move_history': self.move_history,  # История ходов
            'resigned': self.game.resigned  # Флаг сдачи
        }

        try:
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(save_data, f)  # Сериализуем данные
            self.has_saved_game = True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить игру: {str(e)}")

    def new_game(self):
        """Начинает новую игру"""
        self.game = ChessGame()  # Создаем новую игру
        self.move_history = []  # Очищаем историю

        if self.chess_board:  # Если доска уже создана
            self.chess_board.game = self.game  # Обновляем ссылку на игру
            self.chess_board.selected_square = None  # Сбрасываем выбор
            self.chess_board.possible_moves = []  # Очищаем возможные ходы
            self.chess_board.draw_board()  # Перерисовываем доску

        self.update_history_display()  # Обновляем историю
        self.update_status('Новая игра! Ход белых')  # Обновляем статус

        if self.btn_play_again:  # Скрываем кнопку "Сыграть еще раз"
            self.btn_play_again.pack_forget()

    def show_play_again(self):
        """Показывает кнопку 'Сыграть еще раз'"""
        self.btn_play_again.pack(side=tk.RIGHT)
        self.btn_play_again.config(state=tk.NORMAL)

    def resign(self):
        """Обрабатывает сдачу игрока"""
        self.game.resign()  # Устанавливаем флаг сдачи
        # Определяем победителя (противоположный цвет)
        winner = 'Чёрные' if self.game.board.turn == chess.WHITE else 'Белые'
        self.update_status(f'{winner} победили! Игрок сдался.')
        self.show_play_again()  # Показываем кнопку новой игры

    def update_status(self, message=None):
        """Обновляет текстовый статус игры"""
        if message:
            self.status_var.set(message)  # Устанавливаем переданное сообщение
        elif self.game.is_game_over:
            # Если игра окончена, показываем результат
            self.status_var.set(self.game.get_game_result())
            self.show_play_again()  # Показываем кнопку новой игры
        else:
            # Показываем чей сейчас ход
            turn = 'белых' if self.game.board.turn == chess.WHITE else 'чёрных'
            self.status_var.set(f'Ход {turn}')


