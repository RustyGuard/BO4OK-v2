from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.constants import EVENT_SEC
from src.ui.text_label import TextLabel


class FPSCounter(TextLabel):
    def __init__(self, bounds: Rect, font: Font):
        super().__init__(bounds, Color('green'), font, 'FPS:')
        self.frames = 0

    def update(self, event):
        if event.type == EVENT_SEC:
            self.set_text(f'FPS: {self.frames}')
            self.frames = 0

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.frames += 1
