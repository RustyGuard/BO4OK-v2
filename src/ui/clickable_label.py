from functools import partial
from typing import Optional, Callable

from pygame import Color
from pygame.font import Font

from src.ui import UIAnchor, BorderParams
from src.ui.button import UIButton
from src.ui.text_label import TextLabel


class ClickableLabel(UIButton):
    def __init__(self, *,
                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,

                 on_click: Callable[[], None] = None,

                 text: str = '',
                 text_font: Font = None,
                 mouse_hover_text_color: Color = Color('antiquewhite'),
                 mouse_exit_text_color: Color = Color('white')
                 ):
        super().__init__(position=position,
                         size=size,
                         anchor=anchor,
                         color=color,
                         border_params=border_params,
                         on_click=on_click)

        self.label = TextLabel(text=text, text_color=mouse_exit_text_color, font=text_font,
                               position=self.bounds.center, anchor=UIAnchor.CENTER)
        self.append_child(self.label)
        if self.bounds.size == (0, 0):
            self.bounds = self.label.bounds.copy()
        self.on_mouse_hover = partial(self.label.set_text_color, mouse_hover_text_color)
        self.on_mouse_exit = partial(self.label.set_text_color, mouse_exit_text_color)
