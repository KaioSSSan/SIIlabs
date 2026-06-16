import pygame

import board
import checkers
import info
from const import *
from minimax import choose_action as choose_minimax_action, format_action as format_minimax_action
from rl.integration import apply_action_to_game, get_state_from_game, get_valid_actions_from_game


class Class_Game:
    def __init__(self, mode: str = "pvp", agent=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.mode = mode
        self.agent = agent
        self._logged_result = False
        self._allow_human_input = self.mode in ("pvp", "vs_agent")

        # Инициализация компонентов игры
        self.board = board.Class_Board(self.screen)
        self.checkers = checkers.Class_Checkers(self.screen, self.board)
        self.info = info.Info(self.screen)

    def run_game(self):
        while self.running:
            self.handle_events()
            if self.mode == "vs_agent":
                self.play_agent_turn()
            elif self.mode == "agent_vs_minimax":
                self.play_minimax_turn()
                self.play_agent_turn()
            self.render()
            self.check_game_over()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.info.is_button_clicked(event):
                self.checkers.check_end_move()
            if self._allow_human_input:
                self.checkers.handle_events(event)

    def render(self):
        self.board.draw_board()
        self.checkers.draw_checkers()
        self.info.draw_info(self.checkers)
        pygame.display.flip()

    def check_game_over(self):
        self.checkers.check_end_game()
        if self.checkers.game_over_black is not None and self.checkers.game_over_white is not None:
            if self.mode == "agent_vs_minimax" and not self._logged_result:
                self._logged_result = True
                white_wins = int(self.checkers.game_over_white is True) + int(
                    self.checkers.game_over_black is True
                )
                black_wins = int(self.checkers.game_over_white is False) + int(
                    self.checkers.game_over_black is False
                )
                if white_wins > black_wins:
                    result_text = "победа белых(minimax)"
                elif black_wins > white_wins:
                    result_text = "победа черных(agent)"
                else:
                    result_text = "ничья"
                print(f"Итог партии: {result_text}")

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # Пользователь закрыл окно
                        self.running = False
                        return
                self.render()                      # Отрисовываем результаты на экране
                pygame.display.flip()
                self.clock.tick(10)                # Ограничиваем частоту кадров до 10 FPS

    def play_agent_turn(self):
        """Делает ход агента за черных, если его очередь."""
        if self.agent is None:
            return
        if self.checkers.is_white_turn != checkers.MOVE_BLACK:
            return
        if self.checkers.game_over_white is not None and self.checkers.game_over_black is not None:
            return

        safety = 0
        while self.checkers.is_white_turn == checkers.MOVE_BLACK and safety < 100:
            valid_actions = get_valid_actions_from_game(self.checkers)
            if not valid_actions:
                break

            state = get_state_from_game(self.checkers)
            action = self.agent.choose_action(state, valid_actions)
            if action is None:
                break

            apply_action_to_game(self.checkers, action)
            self.checkers.check_end_game()

            if self.checkers.game_over_white is not None and self.checkers.game_over_black is not None:
                break

            safety += 1

    def play_minimax_turn(self):
        """Делает ход минимакса за белых, если его очередь."""
        if self.checkers.is_white_turn != checkers.MOVE_WHITE:
            return
        if self.checkers.game_over_white is not None and self.checkers.game_over_black is not None:
            return

        safety = 0
        while self.checkers.is_white_turn == checkers.MOVE_WHITE and safety < 100:
            action = choose_minimax_action(self.checkers, depth=1)
            if action is None:
                break

            apply_action_to_game(self.checkers, action)
            self.checkers.check_end_game()


            if self.checkers.game_over_white is not None and self.checkers.game_over_black is not None:
                break

            safety += 1
