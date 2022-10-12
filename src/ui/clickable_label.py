from functools import partial

from pygame import Rect, Color
from pygame.font import Font

from src.ui.button import UIButton
from src.ui.text_label import TextLabel


class ClickableLabel(UIButton):
    def __init__(self, bounds, callback_func,
                 text: str,
                 text_font: Font,
                 mouse_hover_text_color: Color,
                 mouse_exit_text_color: Color):
        super().__init__(bounds, None, callback_func)
        self.label = TextLabel(Rect((0, 0), (0, 0)), Color('white'), text_font, text)
        self.append_child(self.label)
        self.on_mouse_hover = partial(self.label.set_color, mouse_hover_text_color)
        self.on_mouse_exit = partial(self.label.set_color, mouse_exit_text_color)

    def update_bounds(self):
        super().update_bounds()
        self.label.absolute_bounds.center = self.absolute_bounds.center
