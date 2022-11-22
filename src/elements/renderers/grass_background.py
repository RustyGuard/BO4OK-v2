import math

import pygame
from pygame import Surface

from src.config import config
from src.core.camera import Camera
from src.ui import UIElement


class GrassBackground(UIElement):
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera
        self.grass_sprite = pygame.image.load('assets/background/grass.png').convert()

    def draw(self, screen: Surface):
        sprite_width = self.grass_sprite.get_width()
        sprite_height = self.grass_sprite.get_height()
        sprites_count = (math.ceil(config.screen.width / sprite_width), math.ceil(config.screen.height / sprite_height))

        for i in range(-1, sprites_count[1]):
            for j in range(-1, sprites_count[0]):
                screen.blit(self.grass_sprite, (self.camera.offset_x % sprite_width + j * sprite_width,
                                                self.camera.offset_y % sprite_height + i * sprite_height))

