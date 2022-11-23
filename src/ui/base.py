from typing import Optional

import pygame
from pygame import Color, Surface
from pygame.event import Event

from src.constants import EVENT_UPDATE, EVENT_SEC
from src.ui import BorderParams, UIAnchor
from src.ui.types import PositionType, SizeType


class UIElement:
    """
    Инициализируется только как контейнер для хранения дочерних элементов
    Для реализации сложного поведения следует наследоваться от этого класса
    """

    def __init__(self, *,
                 position: PositionType = (0, 0),
                 size: SizeType = None,
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

        self._size = size
        self._position = position
        self._anchor = anchor

        self._bounds = anchor.create_rect(position, size)

    def set_position(self, position: PositionType):
        self._position = position
        self._update_bounds()

    def set_size(self, size: SizeType):
        self._size = size
        self._update_bounds()

    def set_anchor(self, anchor: UIAnchor):
        self._anchor = anchor
        self._update_bounds()

    def _update_bounds(self):
        self._bounds = self._anchor.create_rect(self._position, self._size)

    def set_background_color(self, color: Color):
        self.background_color = color

    def update(self, event: Event):
        """
        Возвращение True из этого метода перехватывает событие у других элементов
        Это сделано, чтобы избежать случаев, когда один клик провоцирует два действия у двух разных элементов
        """
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
            if self._bounds.collidepoint(*event.pos):
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
            pygame.draw.rect(screen, self.background_color, self._bounds,
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
            pygame.draw.rect(screen, self.border_params.color, self._bounds,
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
