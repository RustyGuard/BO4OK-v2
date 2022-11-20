from typing import Optional

import pygame
from pygame import Color
from pygame.surface import Surface

from src.ui import UIElement, UIAnchor, BorderParams
from src.ui.types import PositionType, SizeType
from src.utils.image import get_image


class UIImage(UIElement):
    def __init__(self, *,
                 image: str | Surface,

                 position: PositionType = (0, 0),
                 size: SizeType = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 background_color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None):
        if isinstance(image, Surface):
            self.image = image
        else:
            self.image = get_image(image)

        if size is None:
            size = self.image.get_size()
        else:
            self.image = pygame.transform.smoothscale(self.image, size)

        super().__init__(position=position, size=size, anchor=anchor, background_color=background_color,
                         border_params=border_params)

    def draw(self, screen: Surface):
        screen.blit(self.image, self._bounds.topleft)
