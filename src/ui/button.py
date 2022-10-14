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

    def update(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.bounds.collidepoint(*mouse_pos):
                if not self.hovered:
                    self.hovered = True
                    self.on_mouse_hover()
            elif self.hovered:
                self.hovered = False
                self.on_mouse_exit()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.bounds.collidepoint(*event.pos):
                self.callback_func()
                return True
