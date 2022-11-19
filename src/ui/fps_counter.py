from typing import Optional

from pygame import Color
from pygame.font import Font

from src.constants import EVENT_SEC
from src.ui import UIAnchor, BorderParams
from src.ui.text_label import TextLabel, TextAlign


class FPSCounter(TextLabel):
    def __init__(self, *,
                 font: Font = None,
                 text_align: TextAlign = TextAlign.LEFT,  # todo
                 text_color: Color = Color('green'),

                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,
                 ):
        super().__init__(text='FPS:',
                         font=font,
                         text_align=text_align,
                         text_color=text_color,
                         position=position,
                         size=size,
                         anchor=anchor,
                         color=color,
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
