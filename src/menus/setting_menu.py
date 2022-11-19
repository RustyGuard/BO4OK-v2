import pygame
from pygame import Color
from pygame.font import Font

from src.config import config, upload_config_to_disc
from src.main_loop_state import set_main_element
from src.ui import UIElement
from src.ui.button import UIButton
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class SettingsMenu(UIElement):
    def __init__(self):
        super().__init__()

        self.init_menu()

    def init_menu(self):
        self.background = UIImage(image='assets/background/faded_background.png', size=config.screen.size)
        self.append_child(self.background)

        back_button = UIButton(position=(5, 5), size=(75, 75), on_click=self.go_back)
        back_button.append_child(UIImage(image='assets/ui/left-arrow.png',
                                         position=back_button.bounds.topleft,
                                         size=back_button.bounds.size))
        self.append_child(back_button)

        menu_font = Font('assets/fonts/arial.ttf', 40)

        menu = UIElement(position=(150, 150), size=(0, 0))
        self.append_child(menu)

        self.fullscreen = config.screen.fullscreen
        fullscreen_label = TextLabel(text='Полноэкранный режим', text_color=Color('white'), font=menu_font)
        menu.append_child(fullscreen_label)
        self.fullscreen_toggle = UIButton(position=(fullscreen_label.bounds.w, 0),
                                          size=(50, 50),
                                          color=Color('green' if config.screen.fullscreen else 'red'),
                                          on_click=self.toggle_fullscreen)
        menu.append_child(self.fullscreen_toggle)

        self.append_child(ClickableLabel(position=(150, 450), size=(150, 75),
                                         on_click=self.apply_changes,
                                         text='Применить',
                                         text_font=menu_font,
                                         mouse_hover_text_color=Color('antiquewhite'),
                                         mouse_exit_text_color=Color('white')))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.fullscreen_toggle.color = Color('green' if self.fullscreen else 'red')

    def apply_changes(self):
        config.screen.fullscreen = self.fullscreen
        screen = pygame.display.set_mode(config.screen.size, pygame.FULLSCREEN if config.screen.fullscreen else 0)
        config.screen.size = screen.get_size()
        print(screen.get_size())
        self.children.clear()
        self.bounds.size = config.screen.size
        self.init_menu()
        upload_config_to_disc()

    def go_back(self):
        from src.menus.main_menu import MainMenu
        set_main_element(MainMenu())
