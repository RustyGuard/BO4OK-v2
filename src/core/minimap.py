import pygame
from pygame import Color
from pygame.rect import Rect

from src.config import config
from src.core.game import Game
from src.ui import UIElement


class Minimap(UIElement):
    def __init__(self, game: Game):
        self.game = game
        self.mark_size = config['minimap']['mark_size']
        self.mark_color = config['minimap']['mark_color']
        print(self.mark_color)
        super().__init__(Rect(*config['minimap']['bounds']), None)

    def draw(self, screen):
        super().draw(screen)
        mark_rect = Rect(self.absolute_bounds.x, self.absolute_bounds.y, self.mark_size, self.mark_size)
        for unit in self.game.sprites:
            shape = unit.cls_dict.get('mark_shape', 'quad')

            pos = self.worldpos_to_minimap(unit.pos.x, unit.pos.y)
            mark_rect.centerx = self.absolute_bounds.x + pos[0]
            mark_rect.centery = self.absolute_bounds.y + pos[1]

            if shape == 'circle':
                pygame.draw.ellipse(screen, self.mark_color, mark_rect)
                pygame.draw.ellipse(screen, unit.team_color, mark_rect, 2)
            if shape == 'quad':
                pygame.draw.rect(screen, self.mark_color, mark_rect)
                pygame.draw.rect(screen, unit.team_color, mark_rect, 3)

        camera_rect = Rect(
            (self.game.world_size - self.game.camera.offset_x) * self.world_ratio_width,
            (self.game.world_size - self.game.camera.offset_y) * self.world_ratio_height,
            config['screen']['size'][0] * self.world_ratio_width,
            config['screen']['size'][1] * self.world_ratio_height
        )
        pygame.draw.rect(screen, Color('yellow'), camera_rect.move(self.absolute_bounds.x, self.absolute_bounds.y), 1)

    def worldpos_to_minimap(self, x, y):
        return (x + self.game.world_size) * self.world_ratio_width, \
               (y + self.game.world_size) * self.world_ratio_height

    @property
    def world_ratio_width(self):
        return self.relative_bounds.width / (2 * self.game.world_size)

    @property
    def world_ratio_height(self):
        return self.relative_bounds.height / (2 * self.game.world_size)

    def minimap_to_worldpos(self, x, y):
        raise Exception('Not supported')
