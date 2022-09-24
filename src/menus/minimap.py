import pygame
from pygame import Color
from pygame.rect import Rect

from src.components.minimap_icon import MinimapIconComponent
from src.components.position import PositionComponent
from src.config import config
from src.constants import color_name_to_pygame_color
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.ui import UIElement


class Minimap(UIElement):
    def __init__(self, ecs: EntityComponentSystem, camera: Camera):
        self.ecs = ecs
        self.camera = camera
        self.mark_size = config['minimap']['mark_size']
        self.mark_color = config['minimap']['mark_color']
        print(self.mark_color)
        super().__init__(Rect(*config['minimap']['bounds']), None)

    def draw(self, screen):
        super().draw(screen)
        mark_rect = Rect(self.absolute_bounds.x, self.absolute_bounds.y, self.mark_size, self.mark_size)

        position: PositionComponent
        minimap_icon: MinimapIconComponent
        for _, (position, minimap_icon) in self.ecs.get_entities_with_components((PositionComponent, MinimapIconComponent)):
            shape = minimap_icon.mark_shape
            team_color = color_name_to_pygame_color[minimap_icon.team_color_name]

            pos = self.worldpos_to_minimap(position.x, position.y)
            mark_rect.centerx = self.absolute_bounds.x + pos[0]
            mark_rect.centery = self.absolute_bounds.y + pos[1]

            if shape == 'circle':
                pygame.draw.ellipse(screen, self.mark_color, mark_rect)
                pygame.draw.ellipse(screen, team_color, mark_rect, 2)
            elif shape == 'square':
                pygame.draw.rect(screen, self.mark_color, mark_rect)
                pygame.draw.rect(screen, team_color, mark_rect, 3)
            else:
                print(f'Unknown marker shape: {shape}')

        camera_rect = Rect(
            (config['world']['size'] - self.camera.offset_x) * self.world_ratio_width,
            (config['world']['size'] - self.camera.offset_y) * self.world_ratio_height,
            config['screen']['size'][0] * self.world_ratio_width,
            config['screen']['size'][1] * self.world_ratio_height
        )
        pygame.draw.rect(screen, Color('yellow'), camera_rect.move(self.absolute_bounds.x, self.absolute_bounds.y), 1)

    def worldpos_to_minimap(self, x, y):
        return (x + config['world']['size']) * self.world_ratio_width, \
               (y + config['world']['size']) * self.world_ratio_height

    @property
    def world_ratio_width(self):
        return self.relative_bounds.width / (2 * config['world']['size'])

    @property
    def world_ratio_height(self):
        return self.relative_bounds.height / (2 * config['world']['size'])

    def minimap_to_worldpos(self, x, y):
        raise Exception('Not supported')
