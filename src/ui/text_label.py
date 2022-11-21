from enum import Enum, auto
from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.font import Font

from src.ui import UIElement, UIAnchor, BorderParams
from src.ui.types import PositionType


class TextLabel(UIElement):
    def __init__(self, *,
                 text: str,
                 font: Font = None,
                 text_color: Color = Color('black'),

                 position: PositionType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None):
        if font is None:
            font = Font('assets/fonts/arial.ttf', 20)
        self.font = font
        self.text = text
        self.text_color = text_color

        self.text_image = self.font.render(self.text, True, text_color)

        size = self.text_image.get_size()

        super().__init__(position=position, size=size, anchor=anchor, background_color=background_color,
                         border_params=border_params)

    def update_text(self):
        self.text_image = self.font.render(self.text, True, self.text_color)
        self._bounds.size = self.text_image.get_size()
        self._size = self.text_image.get_size()

    def set_text(self, text: str):
        if self.text != text:
            self.text = text
            self.update_text()

    def set_font(self, font: Font):
        self.font = font
        self.update_text()

    def set_text_color(self, color: Color):
        if self.text_color != color:
            self.text_color = color
            self.update_text()

    def draw(self, screen: Surface):
        super().draw(screen)
        screen.blit(self.text_image, self._bounds)
