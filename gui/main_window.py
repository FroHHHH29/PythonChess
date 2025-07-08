import pickle
import chess
import os
import tkinter as tk
from core.game_engine import ChessGame
from gui.board import ChessBoard
from tkinter import messagebox

SAVE_FILE = "chess_save.pkl"

class MainWindow(tk.Tk):
    def __init__(self):#делаем главное окно
        super().__init__()
        self.title("PyChess")
        self.configure(bg='white')
        self.geometry("700x600")

        self.game = ChessGame()
        self.chess_board = None
        self.player_color = chess.WHITE #цвет фигуры игрока по умолчанию
        self.move_history = [] #список с историей ходов (ИСПРАВЛЕНО: history_move -> move_history)
        self.has_saved_game = os.path.exists(SAVE_FILE) #(true/false) проверяем есть ли сохраненная игра

        self.status_var = tk.StringVar() #обновление интерфейса для отображения статуса игры
        self.btn_play_again = None #после шаха и мата кнопка сыграть еще раз

        self.create_start_menu()


    def create_start_menu(self):#начальное меню с кнопками
        self.has_saved_game = os.path.exists(SAVE_FILE)
        for w in self.winfo_children(): #идем по списку дочерних элементов виджетов
            w.destroy()

        frame = tk.Frame(self, bg='white') #создание фрейма
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER) #позицирование фрейма (по центру)

        title = tk.Label( #заголовок игры
            frame,
            text="PyChess",
            font=('Arial', 24, 'bold'),
            bg='white'
        )
        title.pack(pady=20)


        new_game_btn = tk.Button( #кнопка запуска новой игры
            frame,
            text='Новая игра',
            command=self.select_color,
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


        quit_btn = tk.Button( #кнопка выхода из игры
            frame,
            text='Выход',
            command=self.quit,
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#f0d0d0'
        )
        quit_btn.pack(pady=10)

    def select_color(self): #окно выбора цвета фигур
        for w in self.winfo_children():
            w.destroy()

        frame = tk.Frame(self, bg='white')
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label = tk.Label(
            frame,
            text="Выберите цвет фигур",
            font=('Arial', 18),
            bg='white'
        )
        label.pack(pady=20)

        white_btn = tk.Button(
            frame,
            text="Играть белыми",
            command=lambda: self.start_game(chess.WHITE), # функцию start_game передаем белый цвет игрока и запуск
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#f0f0f0'
        )
        white_btn.pack(pady=10)

        black_btn = tk.Button(
            frame,
            text="Играть черными",
            command=lambda: self.start_game(chess.BLACK), # функцию start_game передаем белый цвет игрока и запуск
            font=('Arial', 14),
            width=20,
            height=2,
            bg='#505050',
            fg='white'
        )
        black_btn.pack(pady=10)
#lambda нужна для активации кнопки (вызова функции) только при нажатии на нее, решает проблему с немедленным запуском функции
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

    def start_game(self, player_color): #начинаем игру с выбранным цветом
        self.player_color = player_color
        self.move_history = []  # ИСПРАВЛЕНО: history_move -> move_history
        for w in self.winfo_children(): w.destroy()
        self.create_game_interface()

    def create_game_interface(self): #создаем основной игровой интерфейс
        main_frame = tk.Frame(self) #главный фрейм для доски и истории ходов
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                        #заполнение по
                        #всей доступной
                        #ширине

        board_frame = tk.Frame(main_frame)
        board_frame.pack(side=tk.LEFT, padx=10)
                        #прижимается к левому
                        #краю родительского контейнера

        # ИСПРАВЛЕНО: Передача game и main_window
        self.chess_board = ChessBoard(board_frame, self.game, self, size=500)
        self.chess_board.pack()


        history_frame = tk.LabelFrame(main_frame, text="История ходов", font=('Arial', 12))
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10) #фрейм для истории ходов

        self.history_text = tk.Text(
            history_frame,  #родительский контейнер
            height=20,
            width=20,
            font=('Courier New', 10),
            state=tk.DISABLED #запрет редактирования
        )

        scrollbar = tk.Scrollbar(history_frame, command=self.history_text.yview)
        self.history_text.config(yscrollcommand=scrollbar.set)
        #Обеспечивает двустороннюю связь:
        #При прокрутке текста - ползунок скроллбара двигается
        #При перемещении ползунка - текст прокручивается

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y) #справа растягивается по вертикали
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH) #слева растягивается во все стороны

        self.update_history_display()

        # Панель статуса
        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 12),
            bg='lightgray',
            width=50
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_play_again = tk.Button(
            status_frame,
            text='Сыграть еще раз',
            command=self.new_game,
            state=tk.DISABLED
        )

        # Панель управления
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

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

        color_info = tk.Label(
            control_frame,
            text=f"Ваш цвет: {'белые' if self.player_color == chess.WHITE else 'черные'}",
            font=('Arial', 10),
            padx=10
        )
        color_info.pack(side=tk.RIGHT)

        self.update_status('Ход белых' if self.game.board.turn == chess.WHITE else 'Ход чёрных')

    def load_saved_game(self): #загружаем сохраненную игру
        try:
            with open(SAVE_FILE, 'rb') as f: #открываем файл в бинарном режиме
                save_data = pickle.load(f)
            self.player_color = save_data['player_color']
            self.move_history = save_data['move_history']  # ИСПРАВЛЕНО: move_history
            self.game = ChessGame()
            self.game.board = chess.Board(save_data['fen'])
            self.game.resigned = save_data['resigned']

            for widget in self.winfo_children():
                widget.destroy()
            self.create_game_interface()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить игру: {str(e)}")
            self.has_saved_game = False
            self.create_start_menu()

    def add_move_to_history(self, move): #добавляем ход в историю
        move_str = move.uci()[:4]  #получаем ход без указания превращения в формате uci (e2e3)
        pair_number = len(self.move_history) // 2 + 1  #определяем номер пары

        if len(self.move_history) % 2 == 0:
            #если количество ходов четное (первый шаг - 0) - начинаем новую пару в списке
            self.move_history.append(f"{pair_number}. {move_str}")
        else:
            #если нечетное - добавляем к последней записи в список
            self.move_history[-1] += f" - {move_str}"
            #еобавляем пустую строку для разделения пар
            self.move_history.append("")
        self.update_history_display()

    def update_history_display(self): #обновляем отображение истории ходов
        # 1.разблокируем поле для редактирования
        self.history_text.config(state=tk.NORMAL)

        # 2.полностью очищаем содержимое
        self.history_text.delete(1.0, tk.END)

        # 3.добавляем все ходы из списка истории ходов
        for move in self.move_history:
            self.history_text.insert(tk.END, move + "\n")

        # 4.прокручиваем к концу
        self.history_text.see(tk.END)

        # 5.снова блокируем редактирование
        self.history_text.config(state=tk.DISABLED)

    def return_to_menu(self):
        """Возвращает в главное меню"""
        response = messagebox.askyesnocancel(
            "Выход в меню",
            "Хотите сохранить текущую игру перед выходом?",
            icon='question'
        )

        if response is None:
            return

        if response:
            self.save_game()
        else:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            self.game = ChessGame()
            self.move_history = []
            self.has_saved_game = False

        self.create_start_menu()

    def save_game(self):
        """Сохраняет текущую игру"""
        save_data = {
            'fen': self.game.board.fen(),
            'player_color': self.player_color,
            'move_history': self.move_history,
            'resigned': self.game.resigned
        }

        try:
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(save_data, f)
            self.has_saved_game = True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить игру: {str(e)}")

    def new_game(self):
        """Начинает новую игру"""
        self.game = ChessGame()
        self.move_history = []

        if self.chess_board:
            self.chess_board.game = self.game
            self.chess_board.selected_square = None
            self.chess_board.possible_moves = []
            self.chess_board.draw_board()

        self.update_history_display()
        self.update_status('Новая игра! Ход белых')

        if self.btn_play_again:
            self.btn_play_again.pack_forget()

    def show_play_again(self):
        """Показывает кнопку 'Сыграть еще раз'"""
        self.btn_play_again.pack(side=tk.RIGHT)
        self.btn_play_again.config(state=tk.NORMAL)

    def resign(self):
        """Обрабатывает сдачу игрока"""
        self.game.resign()
        winner = 'Чёрные' if self.game.board.turn == chess.WHITE else 'Белые'
        self.update_status(f'{winner} победили! Игрок сдался.')
        self.show_play_again()

    def update_status(self, message=None):
        """Обновляет статус игры"""
        if message:
            self.status_var.set(message)
        elif self.game.is_game_over:
            self.status_var.set(self.game.get_game_result())
            self.show_play_again()
        else:
            turn = 'белых' if self.game.board.turn == chess.WHITE else 'чёрных'
            self.status_var.set(f'Ход {turn}')