import random

from pygame import mixer
from pygame.mixer import Sound

from src.config import config, upload_config_to_disc


def play_sound(sound_file_path: str, volume: float = 1):
    sound = Sound(sound_file_path)
    sound.set_volume(config.sound.volume * volume * random.uniform(0.5, 1))
    sound.play()


def play_music(music_file_path: str):
    mixer.music.load(music_file_path)
    mixer.music.set_volume(config.sound.volume)
    mixer.music.play()


def set_volume(volume: float):
    assert 0 <= volume <= 1
    config.sound.volume = volume
    mixer.music.set_volume(config.sound.volume)
    upload_config_to_disc()
