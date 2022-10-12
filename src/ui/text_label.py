from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.ui import UIElement


class TextLabel(UIElement):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str):
        self.font = font
        self.text = text
        self.text_image = self.font.render(self.text, True, color)
        if bounds.width == 0 and bounds.height == 0:
            bounds.size = self.text_image.get_size()
        super().__init__(bounds, color)

    def update_text(self):
        self.text_image = self.font.render(self.text, True, self.color)

    def set_text(self, text: str):
        if self.text != text:
            self.text = text
            self.update_text()

    def set_color(self, color: Color):
        if self.color != color:
            self.color = color
            self.update_text()

    def draw(self, screen):
        screen.blit(self.text_image, self.absolute_bounds)