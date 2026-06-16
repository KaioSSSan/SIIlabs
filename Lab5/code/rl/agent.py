import os
import pickle
import random
from collections import defaultdict
from typing import Dict, Iterable, Tuple


class QLearningAgent:
    """Q-learning агент с epsilon-greedy стратегией выбора действия."""

    def __init__(
        self,
        alpha: float = 0.3,
        gamma: float = 0.97,
        epsilon: float = 1.0,
        epsilon_min: float = 0.02,
        epsilon_decay: float = 0.995,
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.q_table = defaultdict(lambda: defaultdict(float))

    def choose_action(self, state, valid_actions):
        """Выбирает действие по epsilon-greedy стратегии."""
        if not valid_actions:
            return None

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        best_value = None
        best_actions = []
        for action in valid_actions:
            value = self.q_table[state][action]
            if best_value is None or value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, next_valid_actions):
        """Обновляет Q-таблицу по формуле Беллмана."""
        if action is None:
            return

        current_q = self.q_table[state][action]
        if next_valid_actions:
            max_next_q = max(self.q_table[next_state][a] for a in next_valid_actions)
        else:
            max_next_q = 0.0

        target = reward + self.gamma * max_next_q
        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def save(self, path: str = "data/q_table.pkl"):
        """Сохраняет Q-таблицу в файл."""
        resolved = self._resolve_path(path)
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "wb") as file:
            pickle.dump(dict(self.q_table), file)

    def load(self, path: str = "data/q_table.pkl"):
        """Загружает Q-таблицу из файла, если он существует."""
        resolved = self._resolve_path(path)
        if not os.path.exists(resolved):
            return
        try:
            with open(resolved, "rb") as file:
                data = pickle.load(file)
        except (EOFError, pickle.UnpicklingError):
            return
        self.q_table = defaultdict(lambda: defaultdict(float), data)

    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        base_dir = os.path.dirname(__file__)
        return os.path.join(base_dir, path)
