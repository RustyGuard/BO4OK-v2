import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.main_loop_state import set_main_element

from src.ui.button import UIButton
from src.ui import UIElement


class PauseMenu(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        self.append_child(UIButton(Rect(0, 0, 150, 150), Color('black'), self.exit_game))

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
