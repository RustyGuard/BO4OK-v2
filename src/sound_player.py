import random

from pygame import mixer
from pygame.mixer import Sound

from src.config import config, upload_config_to_disc
from src.constants import SoundCode

_blockable_playing_sounds: dict[str, Sound] = dict()


def play_sound(sound_code: SoundCode, volume: float = 1):
    sound = Sound(sound_code.value)
    sound.set_volume(config.sound.volume * volume * random.uniform(0.5, 1))
    if sound_code.blocked_by_itself:
        playing_sound = _blockable_playing_sounds.pop(sound_code.name, None)
        if playing_sound is not None:
            playing_sound.stop()

        _blockable_playing_sounds[sound_code.name] = sound
    sound.play()


def play_music(music_file_path: str):
    mixer.music.fadeout(500)
    mixer.music.load(music_file_path)
    mixer.music.set_volume(config.sound.volume)
    mixer.music.play(-1)


def set_volume(volume: float):
    assert 0 <= volume <= 1
    config.sound.volume = volume
    mixer.music.set_volume(config.sound.volume)
    upload_config_to_disc()
