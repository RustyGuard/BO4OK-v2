from dataclasses import dataclass
from enum import Enum


class MarkShape(str, Enum):
    SQUARE = 'square'
    CIRCLE = 'circle'


@dataclass(slots=True)
class MinimapIconComponent:
    mark_shape: MarkShape
    team_color_name: str
    icon_size: int = 5
    icon_border: bool = False
