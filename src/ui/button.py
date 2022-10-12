from typing import Callable

import pygame

from src.ui import UIElement


class UIButton(UIElement):
    def __init__(self, bounds, color, callback_func, *func_args,
                 on_mouse_hover=None,
                 on_mouse_exit=None):
        super().__init__(bounds, color)
        self.callback_func: Callable = callback_func
        self.callback_args = func_args

        self.hovered = False
        self.on_mouse_hover = on_mouse_hover or (lambda: None)
        self.on_mouse_exit = on_mouse_exit or (lambda: None)

    def update(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.absolute_bounds.collidepoint(*mouse_pos):
                if not self.hovered:
                    self.hovered = True
                    self.on_mouse_hover()
            else:
                if self.hovered:
                    self.hovered = False
                    self.on_mouse_exit()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.absolute_bounds.collidepoint(*event.pos):
                self.callback_func(*self.callback_args)
                return True