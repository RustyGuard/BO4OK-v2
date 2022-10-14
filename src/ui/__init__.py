from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.rect import Rect


class UIElement:
    def __init__(self,
                 bounds: Rect = None,
                 color: Optional[Color] = None,
                 border_top_left_radius=-1, border_top_right_radius=-1,
                 border_bottom_left_radius=-1, border_bottom_right_radius=-1,
                 center: tuple[int, int] = None,
                 ):
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        if bounds is None:
            bounds = Rect(0, 0, 0, 0)
        self.bounds = bounds.copy()

        if center is not None:
            self.bounds.center = center

        self.color = color
        self.children = []
        self.enabled = True

    def move(self, x, y):
        self.bounds.move_ip(x, y)

    def update(self, event: Event):
        for elem in reversed(self.children):
            if elem.enabled and elem.update(event):
                return True
        return False

    def render(self, screen: Surface):
        self.draw(screen)
        for elem in self.children:
            if elem.enabled:
                elem.render(screen)

    def draw(self, screen: Surface):
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.bounds,
                             border_top_left_radius=self.border_top_left_radius,
                             border_top_right_radius=self.border_top_right_radius,
                             border_bottom_left_radius=self.border_bottom_left_radius,
                             border_bottom_right_radius=self.border_bottom_right_radius,
                             )

    def append_child(self, child):
        self.children.append(child)

    def shutdown(self):
        pass
