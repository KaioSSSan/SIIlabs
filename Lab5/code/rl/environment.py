import os
from typing import List, Tuple

import pygame

import board as board_module
import checkers as checkers_module
from const import WIDTH, HEIGHT, ROWS, COLS


Action = Tuple[int, int, int, int, int, bool]
State = Tuple[Tuple[Tuple[int, ...], ...], Tuple[Tuple[int, ...], ...], int, int, bool, Tuple[int, int, int, int]]


class CheckersEnv:
    """
    Обертка над существующей логикой шашек Вигмана.

    TODO: При необходимости вынести логику без pygame (headless) в отдельные классы.
    """

    def __init__(self):
        pygame.init()
        self._screen = pygame.Surface((WIDTH, HEIGHT))
        self.board = board_module.Class_Board(self._screen)
        self.checkers = checkers_module.Class_Checkers(self._screen, self.board)

    def reset(self) -> State:
        """Сбрасывает игру в начальное состояние."""
        self.board = board_module.Class_Board(self._screen)
        self.checkers = checkers_module.Class_Checkers(self._screen, self.board)
        return self.get_state()

    def get_state(self) -> State:
        """Преобразует доску и состояние хода в хэшируемый tuple."""
        board_a = tuple(tuple(row) for row in self.checkers.board.boards[0])
        board_b = tuple(tuple(row) for row in self.checkers.board.boards[1])
        return (
            board_a,
            board_b,
            self.checkers.is_white_turn,
            self.checkers.count_move,
            self.checkers.flag_have_chop,
            self._count_pieces(),
        )

    def get_valid_actions(self) -> List[Action]:
        """Возвращает список допустимых ходов для текущего игрока."""
        actions: List[Action] = []
        capture_actions: List[Action] = []

        original_selected = self.checkers.selected_checker
        original_valid = list(self.checkers.valid_moves)
        original_capture = list(self.checkers.capture_moves)

        for board_index, board_state in enumerate(self.checkers.board.boards):
            for row in range(ROWS):
                for col in range(COLS):
                    piece = board_state[row][col]
                    if self._is_current_player_piece(piece):
                        self.checkers.highlight_moves(row, col, board_state)
                        for move in self.checkers.capture_moves:
                            capture_actions.append(
                                (board_index, row, col, move[0], move[1], True)
                            )
                        for move in self.checkers.valid_moves:
                            actions.append(
                                (board_index, row, col, move[0], move[1], False)
                            )

        self.checkers.selected_checker = original_selected
        self.checkers.valid_moves = original_valid
        self.checkers.capture_moves = original_capture

        # Если есть рубка, разрешаем только рубку
        return capture_actions if capture_actions else actions

    def step(self, action: Action) -> Tuple[State, float, bool]:
        """
        Выполняет ход и возвращает (next_state, reward, done).

        TODO: Уточнить правила обязательной рубки между двумя ходами.
        """
        valid_actions = self.get_valid_actions()
        if action not in valid_actions:
            raise ValueError("Недопустимое действие для текущего состояния")

        board_index, from_row, from_col, to_row, to_col, is_capture = action
        board_state = self.checkers.board.boards[board_index]

        current_player = self.checkers.is_white_turn
        before_counts = self._count_pieces()
        reward = 0.0
        before_material = self._material_score(current_player, before_counts)

        self.checkers.selected_checker = (from_row, from_col)
        self.checkers.highlight_moves(from_row, from_col, board_state)

        if is_capture:
            self.checkers.make_capture(to_row, to_col, board_state)
        else:
            self.checkers.make_move(to_row, to_col, board_state)

        after_counts = self._count_pieces()
        after_material = self._material_score(current_player, after_counts)

        captured = self._count_captured(current_player, before_counts, after_counts)
        promoted = self._count_promoted(current_player, before_counts, after_counts)

        reward += 1.0 * captured
        reward += 2.5 * promoted
        reward += 0.3 * (after_material - before_material)
        reward -= 0.02  # небольшой штраф за ход, чтобы агент не затягивал игру

        self.checkers.check_end_game()

        done = (
            self.checkers.game_over_white is not None
            and self.checkers.game_over_black is not None
        )

        if done:
            reward += self._final_reward(current_player)

        return self.get_state(), reward, done

    def _is_current_player_piece(self, piece: int) -> bool:
        """Проверка, принадлежит ли шашка текущему игроку."""
        if self.checkers.is_white_turn == checkers_module.MOVE_WHITE:
            return piece in (checkers_module.W_R, checkers_module.W_Q)
        return piece in (checkers_module.B_R, checkers_module.B_Q)

    def _final_reward(self, player_turn: int) -> float:
        """Награда за результат всей игры (две доски)."""
        winner = self._get_overall_winner()
        if winner is None:
            return 0.0

        if winner and player_turn == checkers_module.MOVE_WHITE:
            return 8.0
        if (not winner) and player_turn == checkers_module.MOVE_BLACK:
            return 8.0
        return -8.0

    def _get_overall_winner(self):
        """Возвращает True для белых, False для черных, None для ничьей."""
        if self.checkers.game_over_white is None or self.checkers.game_over_black is None:
            return None

        if self.checkers.game_over_white == self.checkers.game_over_black:
            return self.checkers.game_over_white

        return None

    def _count_pieces(self) -> Tuple[int, int, int, int]:
        """Возвращает количество (белые, дамки белых, черные, дамки черных)."""
        white_regular = 0
        white_queen = 0
        black_regular = 0
        black_queen = 0

        for board_state in self.checkers.board.boards:
            for row in board_state:
                for piece in row:
                    if piece == checkers_module.W_R:
                        white_regular += 1
                    elif piece == checkers_module.W_Q:
                        white_queen += 1
                    elif piece == checkers_module.B_R:
                        black_regular += 1
                    elif piece == checkers_module.B_Q:
                        black_queen += 1

        return white_regular, white_queen, black_regular, black_queen

    def _count_captured(
        self,
        player_turn: int,
        before: Tuple[int, int, int, int],
        after: Tuple[int, int, int, int],
    ) -> int:
        """Сколько шашек соперника было снято за ход."""
        if player_turn == checkers_module.MOVE_WHITE:
            before_opponent = before[2] + before[3]
            after_opponent = after[2] + after[3]
        else:
            before_opponent = before[0] + before[1]
            after_opponent = after[0] + after[1]
        return max(0, before_opponent - after_opponent)

    def _count_promoted(
        self,
        player_turn: int,
        before: Tuple[int, int, int, int],
        after: Tuple[int, int, int, int],
    ) -> int:
        """Сколько шашек стало дамками за ход."""
        if player_turn == checkers_module.MOVE_WHITE:
            before_queens = before[1]
            after_queens = after[1]
        else:
            before_queens = before[3]
            after_queens = after[3]
        return max(0, after_queens - before_queens)

    def _material_score(self, player_turn: int, counts: Tuple[int, int, int, int]) -> float:
        """Простая оценка материала: дамки ценнее обычных шашек."""
        white_regular, white_queen, black_regular, black_queen = counts
        white_score = white_regular + 2 * white_queen
        black_score = black_regular + 2 * black_queen
        if player_turn == checkers_module.MOVE_WHITE:
            return white_score - black_score
        return black_score - white_score
