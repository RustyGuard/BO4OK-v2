import random

from pygame import Rect


def convert_to_main_angle(angle: int) -> int:
    """Возвращает равный угол в диапазоне [0,360) градусов"""
    while angle >= 360:
        angle -= 360
    while angle < 0:
        angle += 360

    return angle


def rect_by_two_points(p1: tuple[float, float], p2: tuple[float, float]):
    left, right = sorted((p1[0], p2[0]))
    top, bottom = sorted((p1[1], p2[1]))
    return Rect(left, top, right - left, bottom - top)


def spread_position(position: tuple[float, float], spread_distance: int):
    return (position[0] + random.randint(-spread_distance, spread_distance),
            position[1] + random.randint(-spread_distance, spread_distance))


def rotation_direction(angle: int, required_angle: int) -> int:
    if angle == required_angle:
        return 0
    diff = angle - required_angle
    diff = convert_to_main_angle(diff)

    return -1 if diff < 180 else 1


def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value
