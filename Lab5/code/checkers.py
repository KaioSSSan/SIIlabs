from const import *
import pygame

# Загрузка изображений
IMG_WR = pygame.image.load("image/white-regular.png")
IMG_WQ = pygame.image.load("image/white-queen.png")
IMG_BR = pygame.image.load("image/black-regular.png")
IMG_BQ = pygame.image.load("image/black-queen.png")

W_R = 1
B_R = -1
W_Q = 2
B_Q = -2
EMPTY_POLE = 0

MOVE_BLACK = 1
MOVE_WHITE = -1

SOUND_ENABLED = False


class Class_Checkers:
    def __init__(self, screen, board):
        """
        Создание шашек и их обработка
        """
        self.screen = screen
        self.board = board

        self.dragging_sound = None
        if SOUND_ENABLED:
            try:
                self.dragging_sound = pygame.mixer.Sound("sounds/drag_piece.wav")
            except pygame.error:
                self.dragging_sound = None
        self.is_dragging = False

        self.game_over_white = None
        self.game_over_black = None

        # Флаг для отслеживания текущей стороны
        self.is_white_turn = MOVE_WHITE         # Если 1, ход белых, если -1, ход черных
        self.selected_checker = None            # Ссылка на выбранную шашку
        self.count_move = 0
        self.flag_have_chop = False             # обязан рубить после первого хода

        self.valid_moves = []                   # Список допустимых ходов для выбранной шашки
        self.capture_moves = []                 # Список допустимых рубок для выбранной шашки

        self.flag_start_capture = False         # Для отслеживания начала хода при рубке

        self.white_regular = pygame.transform.scale(IMG_WR, (SQUARE_SIZE, SQUARE_SIZE))
        self.black_regular = pygame.transform.scale(IMG_BR, (SQUARE_SIZE, SQUARE_SIZE))
        self.white_queen = pygame.transform.scale(IMG_WQ, (SQUARE_SIZE, SQUARE_SIZE))
        self.black_queen = pygame.transform.scale(IMG_BQ, (SQUARE_SIZE, SQUARE_SIZE))

    def handle_events(self, event):
        # Обрабатываем нажатия мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos)
            # Начало перетаскивания
            self.is_dragging = True
            if self.dragging_sound is not None:
                self.dragging_sound.play()  # Запуск звука
        elif event.type == pygame.MOUSEBUTTONUP:
            # Остановка перетаскивания
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            # Проверяем, происходит ли перемещение мыши
            if self.is_dragging and self.dragging_sound is not None:
                self.dragging_sound.play()  # Воспроизводим звук при перемещении

    def handle_mouse_click(self, position):
        col = position[0] // SQUARE_SIZE
        row = position[1] // SQUARE_SIZE

        if 0 <= col < COLS and 0 <= row < ROWS:
            ##
            if self.is_dragging:
                self.selected_checker(row, col, self.board.boards[(row + col) % 2])
            if self.selected_checker is not None:       # Если выбрана шашка
                if (row, col) in self.valid_moves and not self.flag_have_chop:                                      # Если клик по допустимому ходу
                    self.make_move(row, col, self.board.boards[(row+col) % 2])
                elif (row, col) in self.capture_moves:                                  # Если клик по допустимой рубке
                    if not self.flag_start_capture:
                        self.flag_start_capture = True
                        self.count_move += 1
                    self.make_capture(row, col,  self.board.boards[(row+col) % 2])
                elif not self.flag_have_chop:
                    self.select_checker(row, col, self.board.boards[(row+col) % 2])
            elif not self.flag_have_chop:
                self.select_checker(row, col, self.board.boards[(row + col) % 2])
                if self.flag_start_capture and self.selected_checker is not None:
                    self.flag_start_capture = False

    def select_checker(self, row, col, board):
        """ Проверка на возможность выбрать шашку """
        if self.is_white_turn == MOVE_WHITE:            # Если ход белых
            if board[row][col] in [W_R, W_Q]:
                self.selected_checker = (row, col)
                self.highlight_moves(row, col, board)
        else:                                           # Если ход черных
            if board[row][col] in [B_R, B_Q]:
                self.selected_checker = (row, col)
                self.highlight_moves(row, col, board)

    def highlight_moves(self, row, col, board):
        """
        Подсвечивает все возможные ходы для выбранной шашки.
        """
        self.valid_moves = []
        self.capture_moves = []

        checker = board[row][col]

        if checker in [W_R, B_R]:  # Простая шашка
            self.check_moves(row, col, board)
        elif checker in [W_Q, B_Q]:  # Дамка
            self.check_queen_moves(row, col, board)

    def check_moves(self, row, col, board):
        """
        Проверка возможных ходов для обычной шашки.
        """
        checkers_vrags = [W_R * self.is_white_turn, W_Q * self.is_white_turn]

        simple_move = row + 1 * self.is_white_turn
        if 0 <= simple_move < ROWS:
            if col - 1 >= 0 and board[simple_move][col - 1] == EMPTY_POLE:
                self.valid_moves.append((simple_move, col - 1))  # Ход на пустую клетку
            if col + 1 < COLS and board[simple_move][col + 1] == EMPTY_POLE:
                self.valid_moves.append((simple_move, col + 1))  # Ход на пустую клетку

        # Логика для рубки (если есть шашка противника, через которую можно перепрыгнуть)
        capture = row + 2 * self.is_white_turn
        if 0 <= capture < ROWS:
            if col - 2 >= 0 and (board[simple_move][col - 1] in checkers_vrags) \
                    and board[capture][col - 2] == EMPTY_POLE:
                self.capture_moves.append((capture, col - 2))  # Рубка
            if col + 2 < COLS and (board[simple_move][col + 1] in checkers_vrags) \
                    and board[capture][col + 2] == EMPTY_POLE:
                self.capture_moves.append((capture, col + 2))  # Рубка

        # Логика для рубки назад
        capture = row - 2 * self.is_white_turn
        simple_move = row - 1 * self.is_white_turn
        if 0 <= capture < ROWS:
            if col - 2 >= 0 and (board[simple_move][col - 1] in checkers_vrags) \
                    and board[capture][col - 2] == EMPTY_POLE:
                self.capture_moves.append((capture, col - 2))  # Рубка
            if col + 2 < COLS and (board[simple_move][col + 1] in checkers_vrags) \
                    and board[capture][col + 2] == EMPTY_POLE:
                self.capture_moves.append((capture, col + 2))  # Рубка

    def check_queen_moves(self, row, col, board):
        """
        Проверка возможных ходов для дамки.
        """
        # Дамка может двигаться в любом направлении по диагонали, но не может переступать клетки.
        directions = [(-1, -1), (-1, 1), (1, -1),
                      (1, 1)]  # Направления: вверх-влево, вверх-вправо, вниз-влево, вниз-вправо
        for dr, dc in directions:
            r, c = row, col
            flag_move = True
            capture = False
            while True:
                r += dr
                c += dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if board[r][c] == EMPTY_POLE and flag_move:
                        self.valid_moves.append((r, c))
                    elif 0 <= r + dr < ROWS and 0 <= c + dc < COLS:
                        flag_move = False
                        if not capture:
                            if self.is_white_turn == MOVE_WHITE and board[r][c] in [B_R, B_Q]:
                                if board[r + dr][c + dc] == EMPTY_POLE:
                                    capture = True
                                    self.capture_moves.append((r + dr, c + dc))
                                else:
                                    break
                            elif self.is_white_turn == MOVE_BLACK and board[r][c] in [W_R, W_Q]:
                                if board[r + dr][c + dc] == EMPTY_POLE:
                                    capture = True
                                    self.capture_moves.append((r + dr, c + dc))
                                else:
                                    break
                            else:
                                break
                        else:
                            if board[r + dr][c + dc] == EMPTY_POLE:
                                self.capture_moves.append((r + dr, c + dc))
                            else:
                                break
                    else:
                        break
                else:
                    break

    def check_capture(self, row, col, board):
        """ Проверяет возмоджна ли рубка после первого хода"""
        if self.count_move != 1:
            return

        checker = board[row][col]
        if checker in [W_R, B_R]:  # Простая шашка
            self.check_moves(row, col, board)
        elif checker in [W_Q, B_Q]:  # Дамка
            self.check_queen_moves(row, col, board)

        self.valid_moves = []
        if len(self.capture_moves) != 0:
            self.flag_have_chop = True
            self.selected_checker = (row, col)

    def check_end_move(self):
        """ проверка на окончание хода после нажатия на кнопку """
        if self.count_move == 1:
            self.count_move = 0
            self.is_white_turn *= (-1)
            self.flag_have_chop = False
            self.valid_moves = []
            self.capture_moves = []
            self.selected_checker = None

    def check_end_game(self):
        """
        Проверяет окончание игры на белопольной и чернопольной доске.
        Если у текущего цвета не осталось фигур или они не могут двигаться, игра завершается.
        """

        for idx, board in enumerate(self.board.boards):
            if self.game_over_white is not None and idx == 0:
                continue
            if self.game_over_black is not None and idx == 1:
                continue

            original_valid_moves = self.valid_moves.copy()
            original_capture_moves = self.capture_moves.copy()

            # Определение текущего игрока
            is_white = idx == 0  # Белопольная доска — индекс 0, чернопольная — индекс 1

            white_pieces = 0
            black_pieces = 0
            white_can_move = False
            black_can_move = False

            # Проход по клеткам доски
            for row in range(ROWS):
                for col in range(COLS):
                    piece = board[row][col]

                    if piece in [W_R, W_Q] and self.is_white_turn == MOVE_WHITE:  # Белые фигуры
                        white_pieces += 1
                        if piece == W_R:
                            self.check_moves(row, col, board)
                            if self.valid_moves != [] or self.capture_moves != []:
                                white_can_move = True
                                break
                        if piece == W_Q:
                            self.check_queen_moves(row, col, board)
                            if self.valid_moves != [] or self.capture_moves != []:
                                white_can_move = True
                                break
                    elif piece in [B_R, B_Q] and self.is_white_turn == MOVE_BLACK:  # Черные фигуры
                        black_pieces += 1
                        if piece == B_R:
                            self.check_moves(row, col, board)
                            if self.valid_moves != [] or self.capture_moves != []:
                                black_can_move = True
                                break
                        if piece == B_Q:
                            self.check_queen_moves(row, col, board)
                            if self.valid_moves != [] or self.capture_moves != []:
                                black_can_move = True
                                break

            self.valid_moves = original_valid_moves
            self.capture_moves = original_capture_moves

            # Проверка окончания игры на белопольной доске
            if is_white:
                if self.is_white_turn == MOVE_WHITE and (white_pieces == 0 or not white_can_move):
                    self.game_over_white = False  # Победили черные
                elif self.is_white_turn == MOVE_BLACK and (black_pieces == 0 or not black_can_move):
                    self.game_over_white = True  # Победили белые
            # Проверка окончания игры на чернопольной доске
            else:
                if self.is_white_turn == MOVE_WHITE and (white_pieces == 0 or not white_can_move):
                    self.game_over_black = False  # Победили черные
                elif self.is_white_turn == MOVE_BLACK and (black_pieces == 0 or not black_can_move):
                    self.game_over_black = True  # Победили белые

    def make_move(self, row, col, board):
        """
        Перемещает выбранную шашку на указанную клетку.
        """
        selected_row, selected_col = self.selected_checker
        checker = board[selected_row][selected_col]

        # Перемещаем шашку на новую клетку
        board[selected_row][selected_col] = 0  # Очищаем старую клетку
        board[row][col] = checker  # Помещаем шашку на новую клетку

        # Если шашка достигла конца доски, превращаем её в дамку
        if checker == W_R and row == 0:  # Белая шашка становится дамкой
            board[row][col] = W_Q
        elif checker == B_R and row == ROWS - 1:  # Черная шашка становится дамкой
            board[row][col] = B_Q

        # Передача хода другому игроку
        self.valid_moves = []
        self.capture_moves = []
        self.selected_checker = None
        self.count_move += 1
        if self.count_move == 2:
            self.count_move = 0
            self.is_white_turn *= (-1)
        else:
            # проверяем, можно ли рубить
            self.check_capture(row, col, board)

    def make_capture(self, row, col, board):
        """
        Выполняет рубку шашки противника.
        """
        selected_row, selected_col = self.selected_checker
        checker = board[selected_row][selected_col]

        # Определяем шаги для итерации по направлению рубки
        step_row = 1 if row > selected_row else -1
        step_col = 1 if col > selected_col else -1

        # Очищаем все клетки между начальной и конечной (не включая конечную)
        r, c = selected_row, selected_col
        while (r + step_row, c + step_col) != (row, col):
            r += step_row
            c += step_col
            board[r][c] = EMPTY_POLE  # Заполняем клетку пустым полем

        # Перемещаем шашку на новую клетку
        board[selected_row][selected_col] = EMPTY_POLE

        # Если шашка достигла конца доски, превращаем её в дамку
        if checker == W_R and row == 0:  # Белая шашка становится дамкой
            checker = W_Q
        elif checker == B_R and row == ROWS - 1:  # Черная шашка становится дамкой
            checker = B_Q

        board[row][col] = checker
        # Сбрасываем выделение
        self.selected_checker = (row, col)

        # Проверка возможности продолжения рубки
        self.capture_moves = []
        self.valid_moves = []
        if checker in [W_R, B_R]:  # Простая шашка
            self.check_moves(row, col, board)
        elif checker in [W_Q, B_Q]:  # Дамка
            self.check_queen_moves(row, col, board)

        if self.count_move != 1:
            self.valid_moves = []

        # Если нет возможных продолжений рубки, завершаем ход
        if len(self.capture_moves) == 0:
            if self.count_move == 2:
                self.count_move = 0
                self.is_white_turn *= (-1)
            self.flag_have_chop = False
            self.valid_moves = []
            self.capture_moves = []
            self.selected_checker = None

    def draw_checkers(self):
        """
        Отрисовка шашек на доске.
        """
        for board_state in self.board.boards:
            for row in range(len(board_state)):
                for col in range(len(board_state[row])):
                    checker = board_state[row][col]
                    x = col * SQUARE_SIZE
                    y = row * SQUARE_SIZE

                    # Проверка подсветки выбранной шашки
                    if self.selected_checker == (row, col):
                        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

                    # Отрисовка шашек
                    if checker == W_R:  # Белая шашка
                        self.screen.blit(self.white_regular, (x, y))
                    elif checker == B_R:  # Черная шашка
                        self.screen.blit(self.black_regular, (x, y))
                    elif checker == W_Q:  # Белая дамка
                        self.screen.blit(self.white_queen, (x, y))
                    elif checker == B_Q:  # Черная дамка
                        self.screen.blit(self.black_queen, (x, y))

        # Отрисовка возможных рубок как желтых точек
        for move in self.capture_moves:
            row, col = move
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), SQUARE_SIZE // 8)

        # Отрисовка возможных ходов как красные точки
        for move in self.valid_moves:
            row, col = move
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, (255, 0, 0), (center_x, center_y), SQUARE_SIZE // 8)
