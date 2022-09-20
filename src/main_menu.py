from typing import Optional

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from client import WaitForServerWindow
from src.ui import UIElement, FPSCounter, UIButton, UIPopup


class MainMenu(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):

        super().__init__(rect, color)

        self.main = None
        self.font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), self.font))
        self.append_child(sub_elem)

        btn = UIButton(Rect(15, 15, 150, 75), Color('beige'), self.go_to_client)
        self.append_child(btn)

    def go_to_client(self):
        try:
            w = WaitForServerWindow(self.relative_bounds, self.color)
            self.main.main_element = w
        except ConnectionRefusedError:
            print('Not connected')
            self.append_child(UIPopup(Rect(250, 75, 0, 0), Color('black'), self.font, 'Not connected', 180))
