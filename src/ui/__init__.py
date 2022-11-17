from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.rect import Rect

from src.constants import EVENT_UPDATE, EVENT_SEC


class UIElement:
    def __init__(self,
                 bounds: Rect = None,
                 color: Optional[Color] = None,
                 border_top_left_radius=-1, border_top_right_radius=-1,
                 border_bottom_left_radius=-1, border_bottom_right_radius=-1,
                 border_width=0,
                 border_color=Color('black'),
                 center: tuple[int, int] = None,
                 focusable: bool = False,
                 focused: bool = False
                 ):
        self.border_width = border_width
        self.border_color = border_color

        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        self.focusable = focusable
        self.focused = focused and focusable

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

    def set_color(self, color: Color):
        self.color = color

    def update(self, event: Event):
        if event.type == EVENT_UPDATE:
            self.on_update()

        if event.type == EVENT_SEC:
            self.on_second_passed()

        if event.type == pygame.MOUSEMOTION:
            if self.on_mouse_motion(event.pos, event.rel):
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.on_mouse_button_up(event.pos, event.button):
                return True
            if self.bounds.collidepoint(*event.pos):
                if self.focusable:
                    self.focused = True

                if self.on_mouse_press(event.pos, event.button):
                    return True
            else:
                if self.focusable:
                    self.focused = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.on_mouse_button_down(event.pos, event.button):
                return True

        elif event.type == pygame.KEYUP:
            if self.on_key_up(event.key, event.unicode, event.mod, event.scancode):
                return True

            if (self.focused or not self.focusable) and self.on_key_press(event.key, event.unicode, event.mod,
                                                                        event.scancode):
                return True

        elif event.type == pygame.KEYDOWN:
            if self.on_key_down(event.key, event.unicode, event.mod, event.scancode):
                return True

        for elem in reversed(self.children):
            if elem.enabled and elem.update(event):
                return True
        return False

    def on_update(self):
        pass

    def on_second_passed(self):
        pass

    def on_mouse_motion(self, mouse_position: tuple[int, int], relative_position: tuple[int, int]) -> bool | None:
        pass

    def on_mouse_button_up(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        pass

    def on_mouse_button_down(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        pass

    def on_mouse_press(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        pass

    def on_key_up(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        pass

    def on_key_down(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        pass

    def on_key_press(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        pass

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
        if self.border_width:
            pygame.draw.rect(screen, self.border_color, self.bounds,
                             width=self.border_width,
                             border_top_left_radius=self.border_top_left_radius,
                             border_top_right_radius=self.border_top_right_radius,
                             border_bottom_left_radius=self.border_bottom_left_radius,
                             border_bottom_right_radius=self.border_bottom_right_radius,
                             )

    def append_child(self, child):
        self.children.append(child)

    def shutdown(self):
        pass
