from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from constants import EVENT_SEC


class UIElement:
    def __init__(self, bounds: Rect, color: Optional[Color]):
        self.relative_bounds = bounds
        self.absolute_bounds = bounds.copy()
        self.color = color
        self.childs = []
        self.parent = None

    def update_bounds(self):
        self.absolute_bounds = self.relative_bounds.copy()
        self.absolute_bounds.x = self.absolute_x
        self.absolute_bounds.y = self.absolute_y

        for child in self.childs:
            child.update_bounds()

    @property
    def absolute_x(self):
        if self.parent is None:
            return self.relative_bounds.x
        return self.relative_bounds.x + self.parent.absolute_x

    @property
    def absolute_y(self):
        if self.parent is None:
            return self.relative_bounds.y
        return self.relative_bounds.y + self.parent.absolute_y

    def move(self, x, y):
        self.relative_bounds.move_ip(x, y)
        self.update_bounds()

    def update(self, event):
        for elem in self.childs:
            if elem.update(event):
                return True
        return False

    def render(self, screen):
        self.draw(screen)
        for elem in self.childs:
            elem.render(screen)

    def draw(self, screen):
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.absolute_bounds)

    def append_child(self, child):
        self.childs.append(child)
        child.parent = self
        child.update_bounds()


class Label(UIElement):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str):
        super().__init__(bounds, color)
        self.font = font
        self.text = text
        self.text_image = self.font.render(self.text, True, self.color)

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


class FPSCounter(Label):
    def __init__(self, bounds: Rect, font: Font):
        super().__init__(bounds, Color('green'), font, 'FPS:')
        self.frames = 0

    def update(self, event):
        if event.type == EVENT_SEC:
            print(self.frames)
            self.set_text(f'FPS: {self.frames}')
            self.frames = 0

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.frames += 1
