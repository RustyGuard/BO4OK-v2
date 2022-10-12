from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.constants import EVENT_UPDATE
from src.ui.text_label import TextLabel


class UIPopup(TextLabel):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str, lifetime: int):
        super().__init__(bounds, color, font, text)
        self.life_time = lifetime

    def update(self, event):
        if event.type == EVENT_UPDATE:
            self.life_time -= 1
            if self.life_time <= 0:
                self.parent.childs.remove(self)
                return
        super().update(event)
