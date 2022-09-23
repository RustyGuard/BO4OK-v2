from dataclasses import dataclass


@dataclass(slots=True)
class MinimapIconComponent:
    mark_shape: str
    team_color_name: str
