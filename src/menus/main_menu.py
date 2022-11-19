from pygame import Color
from pygame.font import Font

from src import main_loop_state
from src.config import config
from src.main_loop_state import set_main_element
from src.menus.client.connect_to_game import ConnectToGame
from src.menus.server.host_game import HostGame
from src.menus.setting_menu import SettingsMenu
from src.sound_player import play_music
from src.ui import UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage


class MainMenu(UIElement):
    def __init__(self):
        super().__init__()

        self.font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(UIImage(image='assets/background/menu.png', size=config.screen.size))

        buttons_font = Font('assets/fonts/arial.ttf', 40)
        buttons_data = [
            ('Присоединиться', self.go_to_client),
            ('Создать игру', self.host_server),
            ('Настройки', self.go_to_settings),
            ('Выход', main_loop_state.close_game),
        ]
        buttons_width = config.screen.width // len(buttons_data)
        for i, (button_name, button_action) in enumerate(buttons_data):
            self.append_child(
                ClickableLabel(text=button_name, text_font=buttons_font,
                               position=(buttons_width * i, config.screen.height - 100), size=(buttons_width, 100),
                               on_click=button_action, mouse_hover_text_color=Color('antiquewhite'),
                               mouse_exit_text_color=Color('white')))
        play_music('assets/music/menu.ogg')

    def go_to_client(self):
        set_main_element(ConnectToGame())

    def host_server(self):
        set_main_element(HostGame())

    def go_to_settings(self):
        set_main_element(SettingsMenu())
