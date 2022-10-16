import pygame
from pygame import Rect
from pygame.surface import Surface

from src.ui import UIElement


class UIImage(UIElement):
    def __init__(self, bounds: Rect | None = None, image_path: str = None, image: Surface = None,
                 center: tuple[int, int] = None):
        super().__init__(bounds, None, center=center)
        self.image = pygame.image.load(image_path) if (image_path is not None) else image
        if self.bounds.width != 0 and self.bounds.height != 0:
            self.image = pygame.transform.smoothscale(self.image, self.bounds.size)
        else:
            self.bounds.size = self.image.get_size()

    def draw(self, screen: Surface):
        screen.blit(self.image, self.bounds.topleft)
