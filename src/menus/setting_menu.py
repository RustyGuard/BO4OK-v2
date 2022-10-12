import pygame
from pygame import Rect, Color
from pygame.font import Font

from src import main_loop_state
from src.config import config, upload_config_to_disc
from src.main_loop_state import set_main_element
from src.ui import UIElement, UIImage, UIButton, Label


class SettingsMenu(UIElement):
    def __init__(self, rect: Rect):

        super().__init__(rect, None)

        self.init_menu()

    def init_menu(self):
        self.background = UIImage(self.relative_bounds, 'assets/data/faded_background.png')
        self.append_child(self.background)

        back_button = UIButton(Rect(5, 5, 75, 75), None, self.go_back)
        back_button.append_child(UIImage(back_button.relative_bounds.move(0, 0), 'assets/buttons/left-arrow.png'))
        self.append_child(back_button)

        menu_font = Font('assets/fonts/arial.ttf', 40)

        menu = UIElement(Rect(150, 150, 0, 0), None)
        self.append_child(menu)

        self.fullscreen = config.screen.fullscreen
        fullscreen_label = Label(Rect(0, 0, 0, 0), Color('white'), menu_font, 'Полноэкранный режим ')
        menu.append_child(fullscreen_label)
        self.fullscreen_toggle = UIButton(Rect(fullscreen_label.relative_bounds.w, 0, 50, 50), Color('green' if config.screen.fullscreen else 'red'), self.toggle_fullscreen)
        menu.append_child(self.fullscreen_toggle)

        apply_changes_text = Label(Rect(0, 0, 0, 0), Color('white'), menu_font, 'Применить')
        apply_changes = UIButton(Rect((150, 450), apply_changes_text.relative_bounds.size), None, self.apply_changes)
        apply_changes.append_child(apply_changes_text)
        apply_changes_text.absolute_bounds.center = apply_changes.absolute_bounds.center
        self.append_child(apply_changes)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.fullscreen_toggle.color = Color('green' if self.fullscreen else 'red')

    def apply_changes(self):
        config.screen.fullscreen = self.fullscreen
        screen = pygame.display.set_mode(config.screen.size, pygame.FULLSCREEN if config.screen.fullscreen else 0)
        config.screen.size = screen.get_size()
        print(screen.get_size())
        self.childs.clear()
        self.relative_bounds.size = config.screen.size
        self.init_menu()
        upload_config_to_disc()

    def go_back(self):
        from src.main_menu import MainMenu
        set_main_element(MainMenu(self.relative_bounds))
