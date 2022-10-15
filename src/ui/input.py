import pygame.event
import pyperclip
from pygame import Rect, Color, Surface
from pygame.event import Event
from pygame.font import Font

from src.constants import EVENT_UPDATE
from src.ui import UIElement
from src.ui.text_label import TextLabel


class UIInput(UIElement):
    CURSOR_BLINK_FRAMES = 30

    def __init__(self, bounds: Rect, text_color: Color, background_color: Color, font: Font,
                 center: tuple[int, int] = None, focused: bool = False, limit: int = 10):
        super().__init__(bounds, background_color, center=center)
        self.font = font
        self.value = ''

        self.value_display = TextLabel(None, text_color, self.font, '')
        self.append_child(self.value_display)
        self.value_display.bounds.centery = self.bounds.centery
        self.value_display.bounds.left = self.bounds.left + 5

        self.focused = focused
        self.cursor_blink = self.CURSOR_BLINK_FRAMES
        self.cursor_visible = True
        self.limit = limit

    def set_value(self, value: str):
        self.value = value[:self.limit]
        self.value_display.set_text(self.value)

    def draw(self, screen: Surface):
        super().draw(screen)
        if not self.focused:
            return

        if self.cursor_visible:
            pygame.draw.line(screen, Color('white'), self.value_display.bounds.topright, self.value_display.bounds.bottomright, 2)

    def handle_keyup(self, key_code: int, symbol: str, mod: int):
        if key_code == pygame.K_BACKSPACE:
            if mod & pygame.KMOD_CTRL:
                self.set_value('')
            else:
                self.set_value(self.value[:-1])
            return

        if key_code == pygame.K_v and mod & pygame.KMOD_CTRL:
            symbol = pyperclip.paste()

        if not symbol.isprintable():
            return

        if len(self.value) + len(symbol) > self.limit:
            return

        self.set_value(self.value + symbol)

    def update(self, event: Event):
        if event.type == EVENT_UPDATE:
            self.cursor_blink -= 1
            if self.cursor_blink == 0:
                self.cursor_blink = self.CURSOR_BLINK_FRAMES
                self.cursor_visible = not self.cursor_visible
        if event.type == pygame.MOUSEBUTTONUP:
            is_click_inside = self.bounds.collidepoint(*pygame.mouse.get_pos())
            self.focused = is_click_inside

        if not self.focused:
            return

        if event.type == pygame.KEYUP:
            self.handle_keyup(event.key, event.unicode, event.mod)
