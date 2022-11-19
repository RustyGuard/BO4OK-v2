from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.rect import Rect

from src.constants import EVENT_UPDATE, EVENT_SEC


@dataclass
class BorderParams:
    top_left_radius: int = -1
    top_right_radius: int = -1
    bottom_left_radius: int = -1
    bottom_right_radius: int = -1

    width: int = 1
    color: Color = Color('black')


class UIAnchor(Enum):
    TOP_LEFT = 'topleft'
    TOP_RIGHT = 'topright'
    TOP_MIDDLE = 'midtop'

    CENTER = 'center'

    BOTTOM_LEFT = 'bottomleft'
    BOTTOM_RIGHT = 'bottomright'
    BOTTOM_MIDDLE = 'midbottom'

    MIDDLE_LEFT = 'midleft'
    MIDDLE_RIGHT = 'midright'

    def create_rect(self, position: tuple[int, int], size: tuple[int, int] | None):
        rect = Rect((0, 0), size or (0, 0))
        setattr(rect, self.value, position)
        return rect


class UIElement:
    def __init__(self, *,
                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,

                 focusable: bool = False,
                 focused: bool = False):
        self.background_color = background_color
        self.border_params = border_params

        self.children = []
        self.enabled = True

        self.focusable = focusable
        self.focused = focused and focusable

        self.size = size
        self.position = position
        self.anchor = anchor

        self.bounds = anchor.create_rect(position, size)

    def set_background_color(self, color: Color):
        self.background_color = color

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
        if self.background_color is not None:
            pygame.draw.rect(screen, self.background_color, self.bounds,
                             border_top_left_radius=(
                                 self.border_params.top_left_radius if self.border_params else -1),
                             border_top_right_radius=(
                                 self.border_params.top_right_radius if self.border_params else -1),
                             border_bottom_left_radius=(
                                 self.border_params.bottom_left_radius if self.border_params else -1),
                             border_bottom_right_radius=(
                                 self.border_params.bottom_right_radius if self.border_params else -1),
                             )
        if self.border_params and self.border_params.width:
            pygame.draw.rect(screen, self.border_params.color, self.bounds,
                             width=self.border_params.width,
                             border_top_left_radius=self.border_params.top_left_radius,
                             border_top_right_radius=self.border_params.top_right_radius,
                             border_bottom_left_radius=self.border_params.bottom_left_radius,
                             border_bottom_right_radius=self.border_params.bottom_right_radius,
                             )

    def append_child(self, child):
        self.children.append(child)

    def shutdown(self):
        pass
