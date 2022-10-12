from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src import main_loop_state
from src.menus.client.wait_for_other_players import WaitForServerMenu
from src.config import config
from src.main_loop_state import set_main_element
from src.menus.setting_menu import SettingsMenu
from src.menus.server.wait_for_players_menu import WaitForPlayersMenu
from src.ui.clickable_label import ClickableLabel
from src.ui.popup import UIPopup
from src.ui.image import UIImage
from src.ui import UIElement


class MainMenu(UIElement):
    def __init__(self):
        screen_rect = config.screen.get_rect()
        super().__init__(screen_rect)

        self.font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(UIImage(screen_rect, 'assets/data/menu.png'))

        buttons_font = Font('assets/fonts/arial.ttf', 40)
        buttons_data = [
            ('Присоединиться', self.go_to_client),
            ('Создать игру', self.host_server),
            ('Настройки', self.go_to_settings),
            ('Выход', main_loop_state.close_game),
        ]
        buttons_width = config.screen.width // len(buttons_data)
        for i, (button_name, button_action) in enumerate(buttons_data):
            self.append_child(ClickableLabel(Rect(buttons_width * i, config.screen.height - 100, buttons_width, 100),
                                             button_action, button_name, buttons_font,
                                             mouse_hover_text_color=Color('antiquewhite'),
                                             mouse_exit_text_color=Color('white')))

    def go_to_client(self):
        try:
            set_main_element(WaitForServerMenu())
        except ConnectionRefusedError:
            print('Not connected')
            self.append_child(UIPopup(Rect(250, 75, 0, 0), Color('white'), self.font, 'Not connected', 180))

    def host_server(self):
        set_main_element(WaitForPlayersMenu())

    def go_to_settings(self):
        set_main_element(SettingsMenu(self.relative_bounds))
