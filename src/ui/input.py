from typing import Optional

import pygame.event
import pyperclip
from pygame import Color, Surface
from pygame.font import Font

from src.ui import UIAnchor, BorderParams, UIElement
from src.ui.text_label import TextLabel


class UIInput(UIElement):
    CURSOR_BLINK_FRAMES = 30

    def __init__(self, *,
                 text_color: Color = Color('black'),
                 font: Font,
                 focused: bool = False,
                 max_length: int = 10,

                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None):
        super().__init__(position=position,
                         size=size,
                         anchor=anchor,
                         color=color,
                         border_params=border_params,
                         focusable=True,
                         focused=focused)

        self.value = ''

        self.value_display = TextLabel(text='', text_color=text_color, font=font,
                                       position=self.bounds.move(5, 0).midleft, anchor=UIAnchor.MIDDLE_LEFT)
        self.append_child(self.value_display)

        self.cursor_blink = self.CURSOR_BLINK_FRAMES
        self.cursor_visible = True
        self.max_length = max_length

    def set_value(self, value: str):
        self.value = value[:self.max_length]
        self.value_display.set_text(self.value)

    def draw(self, screen: Surface):
        super().draw(screen)

        if self.focused and self.cursor_visible:
            pygame.draw.line(screen, Color('white'), self.value_display.bounds.topright,
                             self.value_display.bounds.bottomright, 2)

    def on_key_press(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        if key == pygame.K_BACKSPACE:
            if mod & pygame.KMOD_CTRL:
                self.set_value('')
            else:
                self.set_value(self.value[:-1])
            return

        symbol = unicode
        if key == pygame.K_v and mod & pygame.KMOD_CTRL:
            symbol = pyperclip.paste()

        if not symbol.isprintable():
            return

        if len(self.value) + len(symbol) > self.max_length:
            return

        self.set_value(self.value + symbol)

    def on_update(self):
        self.cursor_blink -= 1
        if self.cursor_blink == 0:
            self.cursor_blink = self.CURSOR_BLINK_FRAMES
            self.cursor_visible = not self.cursor_visible
