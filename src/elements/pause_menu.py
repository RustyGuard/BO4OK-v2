import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.config import config
from src.main_loop_state import set_main_element

from src.ui import UIElement
from src.ui.clickable_label import ClickableLabel


class PauseMenu(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        exit_game_label_rect = Rect((0, 0), (150, 75))
        exit_game_label_rect.center = config.screen.get_rect().center
        exit_game_label = ClickableLabel(exit_game_label_rect, self.exit_game,
                                         'Выйти из игры',
                                         pygame.font.SysFont('Comic Sans MS', 20),
                                         mouse_hover_text_color=Color('beige'),
                                         mouse_exit_text_color=Color('white'))

        self.append_child(exit_game_label)

    def exit_game(self):
        from src.menus.main_menu import MainMenu
        set_main_element(MainMenu())

    def render(self, screen: Surface):
        if not self.opened:
            return
        super().render(screen)

    def update(self, event: Event):
        super().update(event)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.opened = not self.opened

        return self.opened
