import pygame
from pygame import Rect, Surface, Color
from pygame.font import Font

from src.components.base.collider import ColliderComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.health import HealthComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.config import config, upload_config_to_disc
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.ui import UIElement, FPSCounter, UIAnchor


class EntitiesRenderer(UIElement):
    def __init__(self, ecs: EntityComponentSystem, camera: Camera):
        super().__init__()
        self.ecs = ecs
        self.camera = camera
        fps_font = Font('assets/fonts/arial.ttf', 30)

        self.fps_counter = FPSCounter(font=fps_font, position=config.screen.rect.move(-5, 5).topright, anchor=UIAnchor.TOP_RIGHT, text_color=Color('lightblue'))
        self.fps_counter.enabled = config.world.show_debug_info
        self.append_child(self.fps_counter)

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

        if config.world.show_debug_info:
            for _, (collider, position) in self.ecs.get_entities_with_components(
                    (ColliderComponent, PositionComponent)):
                pygame.draw.circle(screen, Color('green') if collider.static else Color('lightgreen'),
                                   position.position_according_to_camera(self.camera), collider.radius, 1)


    def on_key_up(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        if key == pygame.K_F3:
            config.world.show_debug_info = not config.world.show_debug_info
            self.fps_counter.enabled = config.world.show_debug_info
            upload_config_to_disc()

            return True
