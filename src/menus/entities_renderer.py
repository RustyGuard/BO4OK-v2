import pygame
from pygame import Rect, Surface, Color

from src.components.base.collider import ColliderComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.health import HealthComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.ui import UIElement


class EntitiesRenderer(UIElement):
    def __init__(self, ecs: EntityComponentSystem, camera: Camera):
        super().__init__(Rect(0, 0, 0, 0), None)
        self.ecs = ecs
        self.camera = camera

    def draw(self, screen: Surface):

        for _, (texture, position) in self.ecs.get_entities_with_components((TextureComponent, PositionComponent)):
            texture.blit(screen, position.position_according_to_camera(self.camera))

        for _, (texture, health, position) in self.ecs.get_entities_with_components(
                (TextureComponent, HealthComponent, PositionComponent)):
            if health.amount == health.max_amount:
                continue
            health_rect = Rect(0, 0, 50, 5)
            health_rect.center = position.position_according_to_camera(self.camera)
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width = health_rect.width * health.amount / health.max_amount
            pygame.draw.rect(screen, Color('red'), health_rect)

        for _, (texture, uncompleted_building, position) in self.ecs.get_entities_with_components(
                (TextureComponent, UncompletedBuildingComponent, PositionComponent)):
            health_rect = Rect(0, 0, 50, 5)
            health_rect.center = position.position_according_to_camera(self.camera)
            health_rect.move_ip(0, -5)
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width = health_rect.width * uncompleted_building.progress / uncompleted_building.required_progress
            pygame.draw.rect(screen, Color('yellow'), health_rect)

        for _, (collider, position) in self.ecs.get_entities_with_components(
                (ColliderComponent, PositionComponent)):
            pygame.draw.circle(screen, Color('green') if collider.static else Color('lightgreen'), position.position_according_to_camera(self.camera), collider.radius, 1)
