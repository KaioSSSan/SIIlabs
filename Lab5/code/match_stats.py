from typing import Tuple

from minimax import choose_action
from rl.agent import QLearningAgent
from rl.environment import CheckersEnv
from rl.integration import apply_action_to_game, get_state_from_game, get_valid_actions_from_game
from rl.trainer import train
import checkers as checkers_module


def _overall_winner(checkers: checkers_module.Class_Checkers):
    if checkers.game_over_white is None or checkers.game_over_black is None:
        return None
    if checkers.game_over_white == checkers.game_over_black:
        return checkers.game_over_white
    return None


def run_agent_vs_minimax_stats(games: int = 100, max_steps: int = 200):
    """Запускает серию партий Agent vs Minimax и печатает итоги."""
    agent = QLearningAgent()
    agent.load()
    if len(agent.q_table) < 2000:
        agent = train(episodes=50000, max_steps=100, save_every=2000, progress_every=1000)
    agent.epsilon = 0.0

    white_wins = 0
    black_wins = 0
    draws = 0

    for game_index in range(1, games + 1):
        env = CheckersEnv()
        env.reset()
        steps = 0
        done = False

        while not done and steps < max_steps:
            if env.checkers.is_white_turn == checkers_module.MOVE_WHITE:
                action = choose_action(env.checkers, depth=1)
            else:
                state = get_state_from_game(env.checkers)
                valid_actions = get_valid_actions_from_game(env.checkers)
                action = agent.choose_action(state, valid_actions) if valid_actions else None

            if action is None:
                break

            apply_action_to_game(env.checkers, action)
            env.checkers.check_end_game()
            done = (
                env.checkers.game_over_white is not None
                and env.checkers.game_over_black is not None
            )
            steps += 1

        winner = _overall_winner(env.checkers)
        if winner is True:
            white_wins += 1
            result_text = "победа белых(minimax)"
        elif winner is False:
            black_wins += 1
            result_text = "победа черных(agent)"
        else:
            draws += 1
            result_text = "ничья"

        print(f"Партия {game_index}: {result_text}")

    print(
        "Итог {0} партий: белые(minimax)={1}, черные(agent)={2}, ничьи={3}".format(
            games,
            white_wins,
            black_wins,
            draws,
        )
    )

    if black_wins > white_wins:
        best = "лучше агент"
    elif white_wins > black_wins:
        best = "лучше минимакс"
    else:
        best = "ничья"

    print(
        "Общий итог: агент выиграл {0} партий, минимакс выиграл {1} партий. {2}.".format(
            black_wins,
            white_wins,
            best,
        )
    )


if __name__ == "__main__":
    run_agent_vs_minimax_stats()
