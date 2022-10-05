from functools import partial
from typing import Optional

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.client.client import WaitForServerWindow
from src.config import config
from src.menus.setting_menu import SettingsMenu
from src.ui import UIElement, FPSCounter, UIButton, UIPopup, UIImage, Label


class MainMenu(UIElement):
    def __init__(self, rect: Rect):

        super().__init__(rect, None)

        self.main = None
        self.font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(UIImage(rect, 'assets/data/menu.png'))

        buttons_font = Font('assets/fonts/arial.ttf', 40)

        for i, (button_name, button_action) in enumerate([
            ('Играть', self.go_to_client),
            ('Настройки', self.go_to_settings),
            ('Выход', self.exit_game),
        ]):
            btn = UIButton(Rect(15 + 275 * i, config.screen.height - 100, 250, 75), None, button_action)
            self.append_child(btn)
            label = Label(Rect((0, 0), (0, 0)), Color('white'), buttons_font, button_name)
            btn.append_child(label)
            label.absolute_bounds.center = btn.absolute_bounds.center
            btn.on_mouse_hover = partial(label.set_color, Color('antiquewhite'))
            btn.on_mouse_exit = partial(label.set_color, Color('white'))

    def go_to_client(self):
        try:
            w = WaitForServerWindow(self.relative_bounds)
            self.main.main_element = w
        except ConnectionRefusedError:
            print('Not connected')
            self.append_child(UIPopup(Rect(250, 75, 0, 0), Color('black'), self.font, 'Not connected', 180))

    def go_to_settings(self):
        self.main.main_element = SettingsMenu(self.relative_bounds)

    def exit_game(self):
        self.main.running = False
