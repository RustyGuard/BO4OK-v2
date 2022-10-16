from src.config import config


def get_sound_volume_from_distance(distance: float):
    return 2 ** (- (distance / config.screen.width * 2) ** 4)
