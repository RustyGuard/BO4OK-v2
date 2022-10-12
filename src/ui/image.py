import pygame

from src.ui import UIElement


class UIImage(UIElement):
    def __init__(self, bounds, image_path, image=None):
        super().__init__(bounds, None)
        self.image = pygame.image.load(image_path) if (image_path is not None) else image
        if bounds.width != 0 and bounds.height != 0:
            self.image = pygame.transform.smoothscale(self.image, self.relative_bounds.size)

    def draw(self, screen):
        screen.blit(self.image, self.absolute_bounds.topleft)