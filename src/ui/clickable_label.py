from functools import partial

from pygame import Rect, Color
from pygame.font import Font

from src.ui.button import UIButton
from src.ui.text_label import TextLabel


class ClickableLabel(UIButton):
    def __init__(self, bounds, callback_func,
                 text: str,
                 text_font: Font,
                 mouse_hover_text_color: Color = Color('antiquewhite'),
                 mouse_exit_text_color: Color = Color('white'),
                 center: tuple[int, int] = None):
        super().__init__(bounds, None, callback_func, center=center)
        self.label = TextLabel(Rect((0, 0), (0, 0)), mouse_exit_text_color, text_font, text, center=self.bounds.center)
        self.append_child(self.label)
        if self.bounds.size == (0, 0):
            self.bounds = self.label.bounds.copy()
        self.on_mouse_hover = partial(self.label.set_color, mouse_hover_text_color)
        self.on_mouse_exit = partial(self.label.set_color, mouse_exit_text_color)
