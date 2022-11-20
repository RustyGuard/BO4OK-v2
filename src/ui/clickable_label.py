from functools import partial
from typing import Optional, Callable

from pygame import Color
from pygame.font import Font

from src.ui import UIAnchor, BorderParams
from src.ui.types import PositionType, SizeType
from src.ui.button import UIButton
from src.ui.text_label import TextLabel


class ClickableLabel(UIButton):
    def __init__(self, *,
                 text: str,
                 text_font: Font = None,

                 position: PositionType = (0, 0),
                 size: SizeType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,

                 on_click: Callable[[], None] = None,
                 mouse_hover_text_color: Color = Color('antiquewhite'),
                 mouse_exit_text_color: Color = Color('white')):
        super().__init__(position=position, size=size, anchor=anchor, background_color=background_color,
                         border_params=border_params, on_click=on_click)

        self.label = TextLabel(text=text, text_color=mouse_exit_text_color, font=text_font,
                               position=self._bounds.center, anchor=UIAnchor.CENTER)
        self.append_child(self.label)
        if size == (0, 0):
            self.set_size(self.label._size)
        self.on_mouse_hover = partial(self.label.set_text_color, mouse_hover_text_color)
        self.on_mouse_exit = partial(self.label.set_text_color, mouse_exit_text_color)
