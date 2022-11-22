from dataclasses import dataclass, field
from typing import Optional, Callable

from pygame import Color

from src.ui import UIElement, UIAnchor, BorderParams
from src.ui.types import PositionType, SizeType
from src.utils.math_utils import clamp


@dataclass(slots=True, frozen=True)
class SliderThumbParams:
    size: SizeType = (5, 5)
    color: Color = field(default_factory=lambda: Color('white'))

    border: BorderParams = None


class _SliderThumb(UIElement):
    def __init__(self, *,
                 thumb_params: SliderThumbParams = SliderThumbParams(),

                 position: PositionType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,
                 ):
        super().__init__(
            position=position,
            size=thumb_params.size,
            anchor=anchor,
            background_color=thumb_params.color,
            border_params=thumb_params.border,
        )
        self.thumb_params = thumb_params

        self.pressed = False

    def on_mouse_button_down(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if self._bounds.collidepoint(*mouse_position) and button == 1:
            self.pressed = True
            return True

    def on_mouse_button_up(self, mouse_position: tuple[int, int], button: int) -> None:
        if button == 1:
            self.pressed = False


class UISlider(UIElement):
    def __init__(self, *,
                 min_value: int = 0,
                 value: int = 50,
                 max_value: int = 100,

                 on_release: Callable[[int], None] = None,  # todo change to on_throttle

                 thumb_params: SliderThumbParams = SliderThumbParams(),

                 position: PositionType = (0, 0),
                 size: SizeType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,
                 ):
        super().__init__(
            position=position,
            size=size,
            anchor=anchor,
            background_color=background_color,
            border_params=border_params,
        )
        assert min_value < max_value, "Неверно указаны крайние значения"
        self.min_value = min_value
        self._value = value
        self.max_value = max_value
        self.on_release = on_release

        self.thumb = _SliderThumb(
            thumb_params=thumb_params,

            anchor=UIAnchor.CENTER,
            position=self.thumb_position,
        )

        self.append_child(self.thumb)

    def get_value(self) -> int:
        return self._value

    def set_value(self, value: int):
        if not (self.min_value <= value <= self.max_value):
            raise ValueError("value outside of range")
        self._value = value
        self.thumb.set_position(self.thumb_position)

    @property
    def thumb_position(self) -> PositionType:
        return (
            self._bounds.left + self._bounds.width * self.normalized_value,
            self._bounds.centery,
        )

    @property
    def normalized_value(self) -> float:
        return (self._value - self.min_value) / (self.max_value - self.min_value)

    @normalized_value.setter
    def normalized_value(self, value: float):
        self.set_value(round((self.max_value - self.min_value) * value + self.min_value))

    def clamp(self, value: int):
        return clamp(value, self.min_value, self.max_value)

    def on_mouse_motion(self, mouse_position: tuple[int, int], relative_position: tuple[int, int]) -> bool | None:
        if not self.thumb.pressed:
            return

        self.normalized_value = clamp((mouse_position[0] - self._bounds.left) / self._bounds.width, 0, 1)

    def on_mouse_button_down(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if self.thumb.pressed:
            return
        if not self._bounds.collidepoint(*mouse_position):
            return
        self.normalized_value = clamp((mouse_position[0] - self._bounds.left) / self._bounds.width, 0, 1)

    def on_mouse_button_up(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if self.thumb.pressed and self.on_release:
            self.on_release(self._value)
