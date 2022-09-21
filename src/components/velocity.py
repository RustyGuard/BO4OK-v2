import math
from dataclasses import dataclass


@dataclass(slots=True)
class VelocityComponent:
    speed_x: float = 0.0
    speed_y: float = 0.0

    @classmethod
    def create_from_polar_coordinates(cls, r: float, angle: int):
        return cls(
            speed_x=math.cos(angle * math.pi / 180) * r,
            speed_y=-math.sin(angle * math.pi / 180) * r,
        )
