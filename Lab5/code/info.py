import pygame


class Info:
    def __init__(self, screen):
        self.screen = screen
        self.info_font_move = pygame.font.Font(None, 36)
        self.end_font_move = pygame.font.Font(None, 25)
        self.button_rect = pygame.Rect(620, 500, 135, 50)  # Координаты и размеры кнопки
        self.button_color = (200, 200, 200)
        self.button_hover_color = (170, 170, 170)

    def draw_info(self, checkers):
        # Отображение текущего игрока
        text = f"Ход: {'Белыx' if checkers.is_white_turn == -1 else 'Чёрныx'}"
        text_surface = self.info_font_move.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (620, 50))

        # Отрисовка результатов на белых полях
        if checkers.game_over_white is not None:
            result_text_white = f"Результат на белых полях: {'Б' if checkers.game_over_white else 'Ч'}"
        else:
            result_text_white = "Результат на белых полях: -"
        result_surface_white = self.info_font_move.render(result_text_white, True, (0, 0, 0))
        self.screen.blit(result_surface_white, (620, 100))

        # Отрисовка результатов на черных полях
        if checkers.game_over_black is not None:
            result_text_black = f"Результат на черных полях: {'Б' if checkers.game_over_black else 'Ч'}"
        else:
            result_text_black = "Результат на черных полях: -"
        result_surface_black = self.info_font_move.render(result_text_black, True, (0, 0, 0))
        self.screen.blit(result_surface_black, (620, 140))

        # Отрисовка общего результата
        if checkers.game_over_white is not None and checkers.game_over_black is not None:
            if checkers.game_over_white == checkers.game_over_black:
                overall_winner = "Белые" if checkers.game_over_white and checkers.game_over_black else "Черные"
            else:
                overall_winner = "Ничья"
            overall_result_text = f"Победитель: {overall_winner}"
        else:
            overall_result_text = "Победитель: -"
        overall_result_surface = self.info_font_move.render(overall_result_text, True, (0, 0, 0))
        self.screen.blit(overall_result_surface, (620, 180))

        # Отрисовка кнопки
        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, color, self.button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_rect, 2)  # Рамка кнопки

        # Текст на кнопке
        button_text = self.end_font_move.render("Закончить ход", True, (0, 0, 0))
        self.screen.blit(button_text, (self.button_rect.x + 5, self.button_rect.y + 5))

    '''def is_button_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False'''

    def is_button_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False

