import math
from dataclasses import dataclass

from src.core.camera import Camera
from src.utils.math_utils import convert_to_main_angle


@dataclass(slots=True)
class PositionComponent:
    x: float
    y: float

    def to_tuple(self):
        return self.x, self.y

    def position_according_to_camera(self, camera: Camera):
        return self.x + camera.offset_x, self.y + camera.offset_y

    def distance(self, other: 'PositionComponent'):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_between(self, other: 'PositionComponent'):
        return convert_to_main_angle(round(-math.atan2(-self.y + other.y, -self.x + other.x) * 180 / math.pi))


def test():
    p1 = PositionComponent(0, 0)
    p2 = PositionComponent(5, 3)
    print(p1.angle_between(p2))
    print(p1.angle_between(PositionComponent(1, 0)))
    print(p1.angle_between(PositionComponent(0, 1)))
    print(p1.angle_between(PositionComponent(-1, 0)))
    print(p1.angle_between(PositionComponent(0, -1)))
    print()
    print(p1.angle_between(PositionComponent(1, 1)))
    print(p1.angle_between(PositionComponent(-1, 1)))


if __name__ == '__main__':
    test()
