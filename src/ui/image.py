from typing import Optional

import pygame
from pygame import Color
from pygame.surface import Surface

from src.ui import UIElement, UIAnchor, BorderParams


class UIImage(UIElement):
    def __init__(self, *,
                 image: str | Surface,

                 position: tuple[int, int] = (0, 0),
                 size: tuple[int, int] = None,
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 color: Optional[Color] = None,
                 border_params: Optional[BorderParams] = None,
                 ):
        if isinstance(image, Surface):
            self.image = image
        else:
            self.image = pygame.image.load(image)

        if size is None:
            size = self.image.get_size()
        else:
            self.image = pygame.transform.smoothscale(self.image, size)

        super().__init__(position=position,
                         size=size,
                         anchor=anchor,
                         color=color,
                         border_params=border_params)

    def draw(self, screen: Surface):
        screen.blit(self.image, self.bounds.topleft)
