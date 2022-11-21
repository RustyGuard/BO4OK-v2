from typing import Optional

from pygame import Color
from pygame.font import Font

from src.constants import EVENT_SEC
from src.ui import UIAnchor, BorderParams
from src.ui.types import PositionType
from src.ui.text_label import TextLabel


class FPSCounter(TextLabel):
    def __init__(self, *,
                 font: Font = None,
                 text_color: Color = Color('green'),

                 position: PositionType = (0, 0),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None):
        super().__init__(text='FPS: 00',
                         font=font,
                         text_color=text_color,
                         position=position,
                         anchor=anchor,
                         background_color=background_color,
                         border_params=border_params)
        self.frames = 0

    def update(self, event):
        if event.type == EVENT_SEC:
            self.set_text(f'FPS: {self.frames}')
            self.frames = 0

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.frames += 1
