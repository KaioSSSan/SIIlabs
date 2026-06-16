import math
from typing import Optional

import checkers as checkers_module
from rl.integration import Action, apply_action_to_game, get_valid_actions_from_game


def choose_action(checkers: checkers_module.Class_Checkers, depth: int = 1) -> Optional[Action]:
    """Выбирает ход минимаксом глубины 1 (по сути жадная оценка)."""
    valid_actions = get_valid_actions_from_game(checkers)
    if not valid_actions:
        return None

    player_turn = checkers.is_white_turn
    best_score = -math.inf
    best_action = valid_actions[0]

    for action in valid_actions:
        snapshot = _snapshot_state(checkers)
        apply_action_to_game(checkers, action)
        checkers.check_end_game()

        score = _evaluate_position(checkers, player_turn)
        winner = _get_overall_winner(checkers)
        if winner is not None:
            if (winner and player_turn == checkers_module.MOVE_WHITE) or (
                (not winner) and player_turn == checkers_module.MOVE_BLACK
            ):
                score += 100.0
            else:
                score -= 100.0

        _restore_state(checkers, snapshot)

        if score > best_score:
            best_score = score
            best_action = action

    return best_action


def format_action(action: Optional[Action]) -> str:
    if action is None:
        return "-"
    board_index, from_row, from_col, to_row, to_col, is_capture = action
    capture_flag = "x" if is_capture else "-"
    return f"B{board_index} ({from_row},{from_col}){capture_flag}({to_row},{to_col})"


def _evaluate_position(checkers: checkers_module.Class_Checkers, player_turn: int) -> float:
    white_regular, white_queen, black_regular, black_queen = _count_pieces(checkers)
    white_score = white_regular + 2 * white_queen
    black_score = black_regular + 2 * black_queen
    if player_turn == checkers_module.MOVE_WHITE:
        return white_score - black_score
    return black_score - white_score


def _count_pieces(checkers: checkers_module.Class_Checkers):
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


def _get_overall_winner(checkers: checkers_module.Class_Checkers):
    if checkers.game_over_white is None or checkers.game_over_black is None:
        return None
    if checkers.game_over_white == checkers.game_over_black:
        return checkers.game_over_white
    return None


def _snapshot_state(checkers: checkers_module.Class_Checkers):
    return {
        "boards": [[row[:] for row in board] for board in checkers.board.boards],
        "is_white_turn": checkers.is_white_turn,
        "count_move": checkers.count_move,
        "flag_have_chop": checkers.flag_have_chop,
        "flag_start_capture": checkers.flag_start_capture,
        "selected_checker": checkers.selected_checker,
        "valid_moves": list(checkers.valid_moves),
        "capture_moves": list(checkers.capture_moves),
        "game_over_white": checkers.game_over_white,
        "game_over_black": checkers.game_over_black,
    }


def _restore_state(checkers: checkers_module.Class_Checkers, snapshot):
    for i, board_state in enumerate(checkers.board.boards):
        for row_index in range(len(board_state)):
            board_state[row_index][:] = snapshot["boards"][i][row_index]

    checkers.is_white_turn = snapshot["is_white_turn"]
    checkers.count_move = snapshot["count_move"]
    checkers.flag_have_chop = snapshot["flag_have_chop"]
    checkers.flag_start_capture = snapshot["flag_start_capture"]
    checkers.selected_checker = snapshot["selected_checker"]
    checkers.valid_moves = snapshot["valid_moves"]
    checkers.capture_moves = snapshot["capture_moves"]
    checkers.game_over_white = snapshot["game_over_white"]
    checkers.game_over_black = snapshot["game_over_black"]

