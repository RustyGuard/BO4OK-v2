import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.config import config
from src.main_loop_state import set_main_element
from src.ui import UIAnchor, UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class PauseMenu(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        fade_image = pygame.Surface(config.screen.rect.size, pygame.SRCALPHA)
        fade_image.fill((0, 0, 0, 100))
        self.append_child(UIImage(image=fade_image, size=config.screen.size))

        menu_bounds = Rect((0, 0), (300, 300))
        menu_bounds.center = config.screen.rect.center

        self.append_child(UIElement(position=config.screen.rect.center, size=(300, 300), anchor=UIAnchor.CENTER, color=Color('gray24')))

        font = pygame.font.SysFont('Comic Sans MS', 20)

        exit_game_label = ClickableLabel(position=config.screen.rect.center, size=(150, 75), anchor=UIAnchor.CENTER,
                                         on_click=self.exit_game,
                                         text='Выйти из игры',
                                         text_font=font,
                                         mouse_hover_text_color=Color('beige'),
                                         mouse_exit_text_color=Color('white'))

        self.append_child(exit_game_label)

        self.append_child(TextLabel(text='Пауза', text_color=Color('slategray'), font=font,
                                    position=menu_bounds.move(0, 15).midtop, anchor=UIAnchor.TOP_MIDDLE))

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
