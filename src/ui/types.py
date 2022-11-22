from dataclasses import dataclass, field
from enum import Enum

from pygame import Color
from pygame.rect import Rect


@dataclass(slots=True)
class BorderParams:
    top_left_radius: int = -1
    top_right_radius: int = -1
    bottom_left_radius: int = -1
    bottom_right_radius: int = -1

    width: int = 1
    color: Color = field(default_factory=lambda: Color('black'))


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


PositionType = tuple[int, int]
SizeType = tuple[int, int]