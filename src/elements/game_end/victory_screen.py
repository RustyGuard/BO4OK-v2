import pygame.draw
from pygame import Surface, Color, Rect
from pygame.event import Event

from src.config import config
from src.main_loop_state import set_main_element
from src.sound_player import play_music
from src.ui import UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage


class VictoryScreen(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        fade_image = pygame.Surface(config.screen.rect.size, pygame.SRCALPHA)
        fade_image.fill((0, 0, 0, 100))
        self.append_child(UIImage(config.screen.rect, image=fade_image))

        image_aspect_ratio = 3.48
        image_width = 500
        self.append_child(UIImage(Rect((0, 0), (image_width, image_width / image_aspect_ratio)), 'assets/ui/game_over/victory.png',
                                  center=config.screen.rect.move(0, -150).center))

        font = pygame.font.SysFont('Comic Sans MS', 20)

        exit_game_label = ClickableLabel(Rect(0, 0, 0, 0), self.exit_game,
                                         'Выйти из игры', font,
                                         mouse_hover_text_color=Color('beige'),
                                         mouse_exit_text_color=Color('white'),
                                         center=config.screen.rect.center)
        self.append_child(exit_game_label)

        close_screen_label = ClickableLabel(Rect(0, 0, 0, 0), self.close_screen,
                                            'Осмотреть свои владения', font,
                                            mouse_hover_text_color=Color('beige'),
                                            mouse_exit_text_color=Color('white'),
                                            center=config.screen.rect.move(0, 50).center)

        self.append_child(close_screen_label)

    def show_screen(self):
        play_music('assets/music/victory.ogg')
        self.opened = True

    def close_screen(self):
        self.opened = False

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

        return self.opened
