def convert_to_main_angle(angle: int) -> int:
    """Возвращает равный угол в диапазоне [0,360) градусов"""
    while angle >= 360:
        angle -= 360
    while angle < 0:
        angle += 360

    return angle
