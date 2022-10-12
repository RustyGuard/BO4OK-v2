from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.rect import Rect


class UIElement:
    def __init__(self, bounds: Rect = None, color: Optional[Color] = None, border_top_left_radius=-1, border_top_right_radius=-1,
                 border_bottom_left_radius=-1, border_bottom_right_radius=-1):
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        if bounds is None:
            bounds = Rect(0, 0, 0, 0)
        self.relative_bounds = bounds
        self.absolute_bounds = bounds.copy()
        self.color = color
        self.childs = []
        self.enabled = True
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

    def update(self, event: Event):
        for elem in reversed(self.childs):
            if elem.enabled and elem.update(event):
                return True
        return False

    def render(self, screen: Surface):
        self.draw(screen)
        for elem in self.childs:
            if elem.enabled:
                elem.render(screen)

    def draw(self, screen: Surface):
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.absolute_bounds,
                             border_top_left_radius=self.border_top_left_radius,
                             border_top_right_radius=self.border_top_right_radius,
                             border_bottom_left_radius=self.border_bottom_left_radius,
                             border_bottom_right_radius=self.border_bottom_right_radius,
                             )

    def append_child(self, child):
        self.childs.append(child)
        child.parent = self
        child.update_bounds()

    def shutdown(self):
        pass