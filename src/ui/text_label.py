from enum import Enum, auto
from typing import Optional

from pygame import Color, Surface
from pygame.font import Font

from src.ui import UIElement, UIAnchor, BorderParams


class TextAlign(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class TextLabel(UIElement):
    def __init__(self, *,
                 text: str,
                 font: Font = None,
                 text_align: TextAlign = TextAlign.CENTER,  # todo
                 text_color: Color = Color('black'),

                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None):
        if font is None:
            font = Font('assets/fonts/arial.ttf', 20)
        self.font = font
        self.text = text
        self.text_color = text_color
        self.text_align = text_align

        self.text_image = self.font.render(self.text, True, text_color)

        if size is None:
            size = self.text_image.get_size()
        # else:
        #     self.text_image =

        super().__init__(position=position, size=size, anchor=anchor, background_color=background_color,
                         border_params=border_params)

    def update_text(self):
        self.text_image = self.font.render(self.text, True, self.text_color)
        self.bounds.size = self.text_image.get_size()

    def set_text(self, text: str):
        if self.text != text:
            self.text = text
            self.update_text()

    def set_text_color(self, color: Color):
        if self.text_color != color:
            self.text_color = color
            self.update_text()

    def draw(self, screen: Surface):
        super().draw(screen)
        screen.blit(self.text_image, self.bounds)
