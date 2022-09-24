import math

from src.components.chase import ChaseComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.utils.math_utils import convert_to_main_angle


def rotation_direction(angle: int, required_angle: int) -> int:
    if angle == required_angle:
        return 0
    diff = angle - required_angle
    diff = convert_to_main_angle(diff)

    return -1 if diff < 180 else 1


def chase_system(chase: ChaseComponent, position: PositionComponent, texture: TextureComponent):
    if chase.chase_position is None:
        return

    if position.distance(chase.chase_position) <= chase.minimal_distance:
        chase.chase_position = None
        return

    angle = position.angle_between(chase.chase_position)

    angle_difference = convert_to_main_angle(texture.rotation_angle - angle)
    if angle_difference > 180:
        angle_difference = 360 - angle_difference

    if angle_difference < chase.rotation_speed:
        texture.rotation_angle = angle

    rotation_dir = rotation_direction(texture.rotation_angle, angle)

    texture.rotation_angle = convert_to_main_angle(texture.rotation_angle + rotation_dir * chase.rotation_speed)

    position.x += math.cos(texture.rotation_angle * math.pi / 180)
    position.y += -math.sin(texture.rotation_angle * math.pi / 180)


def test():
    for i in range(0, 90):
        assert rotation_direction(i, 90) == 1, i
    for i in range(91, 270):
        assert rotation_direction(i, 90) == -1, i

    for i in range(0, 45):
        assert rotation_direction(i, 45) == 1, i
    for i in range(46, 225):
        assert rotation_direction(i, 45) == -1, i


if __name__ == '__main__':
    test()
