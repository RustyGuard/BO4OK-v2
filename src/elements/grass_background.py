import pygame
from pygame import Surface

from src.core.camera import Camera
from src.ui import UIElement


class GrassBackground(UIElement):
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera
        self.grass_sprite = pygame.image.load('assets/sprite/small_map.png').convert()

    def draw(self, screen: Surface):
        sprite_width = self.grass_sprite.get_width()
        sprite_height = self.grass_sprite.get_height()

        for i in range(-1, 2):
            for j in range(-1, 2):
                screen.blit(self.grass_sprite, (self.camera.offset_x % sprite_width + j * sprite_width, self.camera.offset_y % sprite_height + i * sprite_height))

