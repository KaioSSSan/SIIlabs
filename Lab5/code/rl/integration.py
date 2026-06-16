from typing import List, Tuple

import checkers as checkers_module
from const import ROWS, COLS


Action = Tuple[int, int, int, int, int, bool]
State = Tuple[Tuple[Tuple[int, ...], ...], Tuple[Tuple[int, ...], ...], int, int, bool, Tuple[int, int, int, int]]


def get_state_from_game(checkers: checkers_module.Class_Checkers) -> State:
    """Преобразует состояние игры в хэшируемый tuple для Q-таблицы."""
    board_a = tuple(tuple(row) for row in checkers.board.boards[0])
    board_b = tuple(tuple(row) for row in checkers.board.boards[1])
    return (
        board_a,
        board_b,
        checkers.is_white_turn,
        checkers.count_move,
        checkers.flag_have_chop,
        _count_pieces_from_game(checkers),
    )


def get_valid_actions_from_game(checkers: checkers_module.Class_Checkers) -> List[Action]:
    """Возвращает список допустимых ходов из текущего состояния игры."""
    actions: List[Action] = []
    capture_actions: List[Action] = []

    original_selected = checkers.selected_checker
    original_valid = list(checkers.valid_moves)
    original_capture = list(checkers.capture_moves)

    for board_index, board_state in enumerate(checkers.board.boards):
        for row in range(ROWS):
            for col in range(COLS):
                piece = board_state[row][col]
                if _is_current_player_piece(checkers, piece):
                    checkers.highlight_moves(row, col, board_state)
                    for move in checkers.capture_moves:
                        capture_actions.append(
                            (board_index, row, col, move[0], move[1], True)
                        )
                    for move in checkers.valid_moves:
                        actions.append(
                            (board_index, row, col, move[0], move[1], False)
                        )

    checkers.selected_checker = original_selected
    checkers.valid_moves = original_valid
    checkers.capture_moves = original_capture

    return capture_actions if capture_actions else actions


def apply_action_to_game(checkers: checkers_module.Class_Checkers, action: Action):
    """Применяет выбранное действие к текущей игре."""
    board_index, from_row, from_col, to_row, to_col, is_capture = action
    board_state = checkers.board.boards[board_index]

    checkers.selected_checker = (from_row, from_col)
    checkers.highlight_moves(from_row, from_col, board_state)

    if is_capture:
        checkers.make_capture(to_row, to_col, board_state)
    else:
        checkers.make_move(to_row, to_col, board_state)


def _is_current_player_piece(checkers: checkers_module.Class_Checkers, piece: int) -> bool:
    if checkers.is_white_turn == checkers_module.MOVE_WHITE:
        return piece in (checkers_module.W_R, checkers_module.W_Q)
    return piece in (checkers_module.B_R, checkers_module.B_Q)


def _count_pieces_from_game(checkers: checkers_module.Class_Checkers) -> Tuple[int, int, int, int]:
    """Возвращает количество (белые, дамки белых, черные, дамки черных)."""
    white_regular = 0
    white_queen = 0
    black_regular = 0
    black_queen = 0

    for board_state in checkers.board.boards:
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