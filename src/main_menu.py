from functools import partial

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src import main_loop_state
from src.client.client import WaitForServerWindow
from src.config import config
from src.main_loop_state import set_main_element
from src.menus.setting_menu import SettingsMenu
from src.server.server import WaitForPlayersWindow
from src.ui.popup import UIPopup
from src.ui.image import UIImage
from src.ui.button import UIButton
from src.ui.text_label import TextLabel
from src.ui import UIElement


class MainMenu(UIElement):
    def __init__(self, rect: Rect):

        super().__init__(rect, None)

        self.font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(UIImage(rect, 'assets/data/menu.png'))

        buttons_font = Font('assets/fonts/arial.ttf', 40)
        buttons_data = [
            ('Присоединиться', self.go_to_client),
            ('Создать игру', self.host_server),
            ('Настройки', self.go_to_settings),
            ('Выход', main_loop_state.close_game),
        ]
        buttons_width = config.screen.width // len(buttons_data)
        for i, (button_name, button_action) in enumerate(buttons_data):
            btn = UIButton(Rect(buttons_width * i, config.screen.height - 100, buttons_width, 100), None, button_action)
            self.append_child(btn)
            label = TextLabel(Rect((0, 0), (0, 0)), Color('white'), buttons_font, button_name)
            btn.append_child(label)
            label.absolute_bounds.center = btn.absolute_bounds.center
            btn.on_mouse_hover = partial(label.set_color, Color('antiquewhite'))
            btn.on_mouse_exit = partial(label.set_color, Color('white'))

    def go_to_client(self):
        try:
            set_main_element(WaitForServerWindow(self.relative_bounds))
        except ConnectionRefusedError:
            print('Not connected')
            self.append_child(UIPopup(Rect(250, 75, 0, 0), Color('white'), self.font, 'Not connected', 180))

    def host_server(self):
        set_main_element(WaitForPlayersWindow(self.relative_bounds))

    def go_to_settings(self):
        set_main_element(SettingsMenu(self.relative_bounds))
