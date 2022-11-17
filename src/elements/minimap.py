import pygame
from pygame import Color
from pygame.event import Event
from pygame.rect import Rect

from src.components.base.position import PositionComponent
from src.components.minimap_icon import MinimapIconComponent
from src.config import config
from src.constants import color_name_to_pygame_color
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.ui import UIElement


class Minimap(UIElement):
    def __init__(self, ecs: EntityComponentSystem, camera: Camera, player_color: Color):
        self.ecs = ecs
        self.camera = camera
        self.pressed = False
        self.player_color = player_color
        super().__init__(Rect(*config.minimap.bounds), None)
        self.bounds.bottom = config.screen.height

    def update(self, event: Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bounds.collidepoint(pygame.mouse.get_pos()):
                self.pressed = True
                return True
        if event.type == pygame.MOUSEBUTTONUP and self.pressed:
            self.pressed = False
            if self.bounds.collidepoint(pygame.mouse.get_pos()):
                self.move_to_mouse_click()
            return True

    def move_to_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()
        relative_mouse_pos = mouse_pos[0] - self.bounds.x, mouse_pos[1] - self.bounds.y
        self.camera.set_center(self.minimap_to_worldpos(*relative_mouse_pos))

    def draw(self, screen):
        super().draw(screen)

        for _, (position, minimap_icon) in self.ecs.get_entities_with_components((PositionComponent, MinimapIconComponent)):
            mark_rect = Rect(0, 0, minimap_icon.icon_size, minimap_icon.icon_size)
            shape = minimap_icon.mark_shape
            team_color = color_name_to_pygame_color[minimap_icon.team_color_name]

            pos = self.worldpos_to_minimap(position.x, position.y)
            mark_rect.centerx = self.bounds.x + pos[0]
            mark_rect.centery = self.bounds.y + pos[1]

            if shape == 'circle':
                pygame.draw.ellipse(screen, team_color, mark_rect)
                if minimap_icon.icon_border:
                    pygame.draw.ellipse(screen, Color('white'), mark_rect, 1)
            elif shape == 'square':
                pygame.draw.rect(screen, team_color, mark_rect)
                if minimap_icon.icon_border:
                    pygame.draw.rect(screen, Color('white'), mark_rect, 1)
            else:
                print(f'Unknown marker shape: {shape}')

        camera_rect = Rect(
            (config.world.size - self.camera.offset_x) * self.world_ratio_width,
            (config.world.size - self.camera.offset_y) * self.world_ratio_height,
            config.screen.size[0] * self.world_ratio_width,
            config.screen.size[1] * self.world_ratio_height
        )
        pygame.draw.rect(screen, self.player_color, camera_rect.move(self.bounds.x, self.bounds.y), 1)

    def worldpos_to_minimap(self, x, y):
        return (x + config.world.size) * self.world_ratio_width, \
               (y + config.world.size) * self.world_ratio_height

    @property
    def world_ratio_width(self):
        return self.bounds.width / (2 * config.world.size)

    @property
    def world_ratio_height(self):
        return self.bounds.height / (2 * config.world.size)

    def minimap_to_worldpos(self, x, y):
        normalized_x = 2 * x / self.bounds.w - 1
        normalized_y = 2 * y / self.bounds.h - 1

        return -normalized_x * config.world.size, -normalized_y * config.world.size
