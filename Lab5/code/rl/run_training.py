import argparse
import os
import sys

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

from rl.agent import QLearningAgent
from rl.trainer import train


if __name__ == "__main__":
    # Быстрый запуск обучения из консоли
    parser = argparse.ArgumentParser(description="Обучение агента Q-learning")
    parser.add_argument("--episodes", type=int, default=50000, help="Количество эпизодов")
    parser.add_argument("--save-every", type=int, default=1000, help="Частота сохранения")
    parser.add_argument("--progress-every", type=int, default=200, help="Частота вывода прогресса")
    parser.add_argument("--max-steps", type=int, default=100, help="Максимум шагов в эпизоде")
    args = parser.parse_args()

    try:
        train(
            episodes=args.episodes,
            save_every=args.save_every,
            progress_every=args.progress_every,
            max_steps=args.max_steps,
        )
    except KeyboardInterrupt:
        # Сохраняем таблицу на всякий случай
        agent = QLearningAgent()
        agent.load()
        agent.save()
        print("Обучение прервано. Q-таблица сохранена.")
