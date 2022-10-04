import math

from src.components.chase import ChaseComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.utils.math_utils import convert_to_main_angle, rotation_direction

FORCE_MOVE_DISTANCE_FROM_AIM = 50


def chase_system(chase: ChaseComponent, position: PositionComponent, texture: TextureComponent):
    if chase.chase_position is None:
        return

    angle = position.angle_between(chase.chase_position)

    angle_difference = convert_to_main_angle(texture.rotation_angle - angle)
    if angle_difference > 180:
        angle_difference = 360 - angle_difference

    if angle_difference < chase.rotation_speed:
        texture.rotation_angle = angle

    rotation_dir = rotation_direction(texture.rotation_angle, angle)

    texture.rotation_angle = convert_to_main_angle(texture.rotation_angle + rotation_dir * chase.rotation_speed)

    if chase.entity_id is None:
        if position.distance(chase.chase_position) <= FORCE_MOVE_DISTANCE_FROM_AIM:
            chase.chase_position = None
            return
    else:
        if position.distance(chase.chase_position) <= chase.distance_until_attack:
            return

    position.x += math.cos(texture.rotation_angle * math.pi / 180)
    position.y += -math.sin(texture.rotation_angle * math.pi / 180)
