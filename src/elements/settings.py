from typing import Callable

from pygame import Color, mixer
from pygame.font import Font

from src.config import config, upload_config_to_disc
from src.ui import UIElement, UIAnchor, BorderParams, UISlider, TextLabel
from src.ui.slider import SliderThumbParams
from src.ui.types import PositionType


class SettingsElement(UIElement):
    def __init__(self, position: PositionType = None, on_apply: Callable[[], None] = None):
        if position is None:
            position = config.screen.rect.center
        self._on_apply = on_apply
        super().__init__(position=position)
        menu_font = Font('assets/fonts/arial.ttf', 40)

        sound_label = TextLabel(position=config.screen.rect.move(-15, -50).center,
                                anchor=UIAnchor.MIDDLE_RIGHT,
                                text='Громкость',
                                text_color=Color('white'),
                                font=menu_font)
        self.append_child(sound_label)

        self.volume_slider = UISlider(position=config.screen.rect.move(15, -50).center,
                                      size=(200, 15),
                                      min_value=0,
                                      value=round(config.sound.volume * 100),
                                      max_value=100,
                                      on_release=self.set_volume,
                                      anchor=UIAnchor.MIDDLE_LEFT,
                                      background_color=Color('lightgray'),
                                      border_params=BorderParams(
                                          width=1,
                                          color=Color('black'),
                                          bottom_left_radius=5,
                                          bottom_right_radius=5,
                                          top_left_radius=5,
                                          top_right_radius=5,
                                      ),
                                      thumb_params=SliderThumbParams(
                                          size=(15, 50),
                                          color=Color('white'),
                                          border=BorderParams(
                                              width=1,
                                              color=Color('black'),
                                              bottom_left_radius=5,
                                              bottom_right_radius=5,
                                              top_left_radius=5,
                                              top_right_radius=5,
                                          )
                                      ))

        self.append_child(self.volume_slider)

    def set_volume(self, volume: int):
        config.sound.volume = volume / 100
        mixer.music.set_volume(config.sound.volume)
        upload_config_to_disc()

