import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.config import config
from src.elements.settings import SettingsElement
from src.main_loop_state import set_main_element
from src.ui import UIAnchor, UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class PauseMenu(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        settings = SettingsElement()

        fade_image = pygame.Surface(config.screen.rect.size, pygame.SRCALPHA)
        fade_image.fill((0, 0, 0, 100))
        fade_image_element = UIImage(image=fade_image, size=config.screen.size)

        font = pygame.font.SysFont('Comic Sans MS', 40)

        exit_game_label = ClickableLabel(text='Выйти из игры',
                                         text_font=font,
                                         position=config.screen.rect.move(0, 150).center,
                                         anchor=UIAnchor.CENTER,
                                         on_click=self.exit_game,
                                         mouse_hover_text_color=Color('beige'),
                                         mouse_exit_text_color=Color('white'))
        pause_label = TextLabel(text='Пауза',
                                text_color=Color('slategray'),
                                font=font,
                                position=config.screen.rect.move(0, -250).center,
                                anchor=UIAnchor.TOP_MIDDLE)

        self.append_child(fade_image_element)

        background_element = UIElement(position=config.screen.rect.center,
                                       size=(600, 500),
                                       anchor=UIAnchor.CENTER,
                                       background_color=Color('gray24'))
        self.append_child(background_element)

        self.append_child(exit_game_label)

        self.append_child(pause_label)

        self.append_child(settings)

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
