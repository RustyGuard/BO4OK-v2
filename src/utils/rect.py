from pygame import Rect


def rect_with_center(center: tuple[float, float], size: tuple[float, float]):
    rect = Rect((0, 0), size)
    rect.center = center
    return rect
