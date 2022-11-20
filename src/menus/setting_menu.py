from src.config import config
from src.elements.settings import SettingsElement
from src.main_loop_state import set_main_element
from src.ui import UIElement
from src.ui.button import UIButton
from src.ui.image import UIImage


class SettingsMenu(UIElement):
    def __init__(self):
        super().__init__()

        self.init_menu()

    def init_menu(self):
        self.children.clear()
        self.background = UIImage(image='assets/background/faded_background.png', size=config.screen.size)
        self.append_child(self.background)

        back_button = UIButton(position=(5, 5), size=(75, 75), on_click=self.go_back)
        back_button.append_child(UIImage(image='assets/ui/left-arrow.png',
                                         position=back_button._bounds.topleft,
                                         size=back_button._bounds.size))
        self.append_child(back_button)

        self.append_child(SettingsElement(on_apply=self.init_menu))

    def go_back(self):
        from src.menus.main_menu import MainMenu
        set_main_element(MainMenu())
