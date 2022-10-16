from typing import Callable

import pygame

from src.ui import UIElement


class UIButton(UIElement):
    def __init__(self, bounds, color, callback_func,
                 on_mouse_hover=None,
                 on_mouse_exit=None,
                 center: tuple[int, int] = None):
        super().__init__(bounds, color, center=center)
        self.callback_func: Callable = callback_func

        self.hovered = False
        self.on_mouse_hover = on_mouse_hover or (lambda: None)
        self.on_mouse_exit = on_mouse_exit or (lambda: None)

    def on_mouse_motion(self, mouse_position: tuple[int, int], relative_position: tuple[int, int]) -> None:
        if self.bounds.collidepoint(*mouse_position):
            if not self.hovered:
                self.hovered = True
                self.on_mouse_hover()
        elif self.hovered:
            self.hovered = False
            self.on_mouse_exit()

    def on_mouse_press(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if button == 1:
            self.callback_func()
            return True
