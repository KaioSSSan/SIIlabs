from typing import Optional

from rl.agent import QLearningAgent
from rl.environment import CheckersEnv


def train(
    episodes: int = 10000,
    save_every: int = 1000,
    progress_callback=None,
    progress_every: int = 200,
    max_steps: int = 100,
) -> QLearningAgent:
    """
    Обучает агента игре в шашки Вигмана.

    Агент играет сам с собой, используя одну Q-таблицу для обеих сторон.
    """
    env = CheckersEnv()
    agent = QLearningAgent()
    agent.load()

    for episode in range(1, episodes + 1):
        state = env.reset()
        done = False
        total_reward = 0.0
        steps = 0
        last_action = None
        last_player = env.checkers.is_white_turn
        while not done:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                # Нет ходов — считаем поражением текущего игрока
                reward = -2.0
                next_state = env.get_state()
                agent.update(state, None, reward, next_state, [])
                total_reward += reward
                done = True
                break

            action = agent.choose_action(state, valid_actions)
            last_action = action
            last_player = env.checkers.is_white_turn

            next_state, reward, done = env.step(action)
            next_valid_actions = env.get_valid_actions() if not done else []

            agent.update(state, action, reward, next_state, next_valid_actions)
            state = next_state
            total_reward += reward
            steps += 1

            if steps >= max_steps:
                total_reward -= 0.5  # штраф за слишком длинную партию
                done = True
                break

        agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

        if progress_callback is not None and (episode % progress_every == 0 or episode == episodes):
            try:
                should_continue = progress_callback(
                    episode,
                    total_reward,
                    agent.epsilon,
                    last_action,
                    last_player,
                    steps,
                )
            except TypeError:
                should_continue = progress_callback(episode, total_reward, agent.epsilon)
            if should_continue is False:
                break

        if episode % save_every == 0:
            print(f"Эпизод {episode}: суммарная награда = {total_reward:.2f}")
            agent.save()

    agent.save()
    return agent


def prepare_agent(episodes: int = 20000) -> QLearningAgent:
    """
    Возвращает агента с загруженной Q-таблицей.

    Если файла нет — запускает обучение.
    """
    agent = QLearningAgent()
    agent.load()

    if not agent.q_table:
        agent = train(episodes=episodes)

    # Для игры фиксируем epsilon в 0, чтобы агент играл по лучшим ходам
    agent.epsilon = 0.0
    return agent