from typing import Optional, Callable

from pygame import Color, Surface

from src.ui import UIButton, UIAnchor, BorderParams, UIImage
from src.ui.types import PositionType, SizeType


class UICheckBox(UIButton):
    def __init__(self, *,
                 position: PositionType = (0, 0),
                 size: SizeType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 value: bool = False,

                 unselected_background_color: Optional[Color] = None,
                 selected_background_color: Optional[Color] = None,
                 check_image: str | Surface | None = 'assets/ui/checkbox/check.png',

                 border_params: Optional[BorderParams] = None,

                 on_change: Callable[[bool], None] = None,
                 ):
        self.unselected_background_color = unselected_background_color
        self.selected_background_color = selected_background_color
        self._value = value
        self.on_change = on_change

        super(UICheckBox, self).__init__(
            position=position,
            size=size,
            anchor=anchor,
            background_color=self.get_background_color(),
            border_params=border_params,
            on_click=self.on_click,
            # on_mouse_hover=on_mouse_hover,
            # on_mouse_exit=on_mouse_exit,
        )

        if isinstance(check_image, (Surface, str)):
            self.check = UIImage(image=check_image,
                                 position=position,
                                 size=size,
                                 anchor=anchor)
            self.append_child(self.check)
            self.check.enabled = value
        else:
            self.check = None

    def get_value(self) -> bool:
        return self._value

    def get_background_color(self):
        return self.selected_background_color if self._value else self.unselected_background_color

    def set_value(self, value: bool):
        self._value = value
        self.background_color = self.get_background_color()
        if self.check:
            self.check.enabled = value
        if self.on_change:
            self.on_change(self._value)

    def on_click(self):
        self.set_value(not self._value)
