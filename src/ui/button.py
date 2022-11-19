from typing import Callable, Optional

from pygame import Color

from src.ui import UIElement, UIAnchor, BorderParams


class UIButton(UIElement):
    def __init__(self, *,
                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,

                 on_click: Callable[[], None] = None,

                 on_mouse_hover=None,
                 on_mouse_exit=None):

        super().__init__(position=position,
                         size=size,
                         anchor=anchor,
                         color=color,
                         border_params=border_params)

        self._callback_func = on_click

        self.hovered = False
        self.on_mouse_hover = on_mouse_hover or (lambda: None)
        self.on_mouse_exit = on_mouse_exit or (lambda: None)

    def set_callback_function(self, func: Callable[[], None]):
        self._callback_func = func

    def on_mouse_motion(self, mouse_position: tuple[int, int], relative_position: tuple[int, int]) -> None:
        if self.bounds.collidepoint(*mouse_position):
            if not self.hovered:
                self.hovered = True
                self.on_mouse_hover()
        elif self.hovered:
            self.hovered = False
            self.on_mouse_exit()

    def on_mouse_press(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if self._callback_func and button == 1:
            self._callback_func()
            return True
