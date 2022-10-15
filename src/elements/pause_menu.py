import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.config import config
from src.main_loop_state import set_main_element

from src.ui import UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class PauseMenu(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        fade_image = pygame.Surface(config.screen.rect.size, pygame.SRCALPHA)
        fade_image.fill((0, 0, 0, 100))
        self.append_child(UIImage(config.screen.rect, image=fade_image))

        menu_bounds = Rect((0, 0), (300, 300))
        menu_bounds.center = config.screen.rect.center

        self.append_child(UIElement(menu_bounds.copy(), Color('gray24')))

        font = pygame.font.SysFont('Comic Sans MS', 20)

        exit_game_label = ClickableLabel(Rect(0, 0, 150, 75), self.exit_game,
                                         'Выйти из игры', font,
                                         mouse_hover_text_color=Color('beige'),
                                         mouse_exit_text_color=Color('white'),
                                         center=config.screen.rect.center)

        self.append_child(exit_game_label)

        pause_label = TextLabel(None, Color('slategray'), font, 'Пауза', center=config.screen.rect.center)
        pause_label.bounds.centerx = menu_bounds.centerx
        pause_label.bounds.centery = menu_bounds.top + 45
        self.append_child(pause_label)

    def exit_game(self):
        from src.menus.main_menu import MainMenu
        set_main_element(MainMenu())

    def render(self, screen: Surface):
        if not self.opened:
            return
        super().render(screen)

    def update(self, event: Event):
        if self.opened:
            super().update(event)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.opened = not self.opened

        return self.opened
