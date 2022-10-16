import pygame.event
import pyperclip
from pygame import Rect, Color, Surface
from pygame.font import Font

from src.ui import UIElement
from src.ui.text_label import TextLabel


class UIInput(UIElement):
    CURSOR_BLINK_FRAMES = 30

    def __init__(self, bounds: Rect, text_color: Color, background_color: Color, font: Font,
                 center: tuple[int, int] = None, focused: bool = False, limit: int = 10):
        super().__init__(bounds, background_color, center=center, focusable=True, focused=focused)
        self.font = font
        self.value = ''

        self.value_display = TextLabel(None, text_color, self.font, '')
        self.append_child(self.value_display)
        self.value_display.bounds.centery = self.bounds.centery
        self.value_display.bounds.left = self.bounds.left + 5

        self.cursor_blink = self.CURSOR_BLINK_FRAMES
        self.cursor_visible = True
        self.limit = limit

    def set_value(self, value: str):
        self.value = value[:self.limit]
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

        if len(self.value) + len(symbol) > self.limit:
            return

        self.set_value(self.value + symbol)

    def on_update(self):
        self.cursor_blink -= 1
        if self.cursor_blink == 0:
            self.cursor_blink = self.CURSOR_BLINK_FRAMES
            self.cursor_visible = not self.cursor_visible
