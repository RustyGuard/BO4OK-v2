import pygame.draw
from pygame import Surface, Color
from pygame.event import Event

from src.config import config
from src.main_loop_state import set_main_element
from src.sound_player import play_music
from src.ui import UIAnchor, UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage


class DefeatScreen(UIElement):
    def __init__(self):
        super().__init__()
        self.opened = False

        fade_image = pygame.Surface(config.screen.rect.size, pygame.SRCALPHA)
        fade_image.fill((0, 0, 0, 100))
        self.append_child(UIImage(image=fade_image, size=config.screen.rect.size))

        image_aspect_ratio = 5.72
        image_width = 500
        self.append_child(UIImage(image='assets/ui/game_over/loose.png',
                                  position=config.screen.rect.move(0, -150).center,
                                  size=(image_width, int(image_width / image_aspect_ratio)),
                                  anchor=UIAnchor.CENTER))

        font = pygame.font.SysFont('Comic Sans MS', 20)

        exit_game_label = ClickableLabel(text='Выйти из игры', text_font=font, position=config.screen.rect.center,
                                         anchor=UIAnchor.CENTER, on_click=self.exit_game,
                                         mouse_hover_text_color=Color('beige'), mouse_exit_text_color=Color('white'))
        self.append_child(exit_game_label)

        close_screen_label = ClickableLabel(text='Продолжить в качестве наблюдателя', text_font=font,
                                            position=config.screen.rect.move(0, 50).center, anchor=UIAnchor.CENTER,
                                            on_click=self.close_screen, mouse_hover_text_color=Color('beige'),
                                            mouse_exit_text_color=Color('white'))

        self.append_child(close_screen_label)

    def show_screen(self):
        play_music('assets/music/defeat.ogg')
        self.opened = True

    def close_screen(self):
        play_music('assets/music/game1.ogg')
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
