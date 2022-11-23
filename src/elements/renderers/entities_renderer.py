import pygame
from pygame import Rect, Surface, Color
from pygame.font import Font

from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.core_building import CoreBuildingComponent
from src.components.fighting.health import HealthComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.config import config, upload_config_to_disc
from src.constants import color_name_to_pygame_color
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo
from src.ui import UIElement, FPSCounter, UIAnchor


class EntitiesRenderer(UIElement):
    def __init__(self, ecs: EntityComponentSystem, camera: Camera, players: dict[int, PlayerInfo]):
        super().__init__()
        self._ecs = ecs
        self._camera = camera
        self._players = players
        fps_font = Font('assets/fonts/arial.ttf', 30)
        self._nicks_font = pygame.font.SysFont('Comic Sans MS', 30)

        self._fps_counter = FPSCounter(font=fps_font, position=config.screen.rect.move(-5, 5).topright,
                                       anchor=UIAnchor.TOP_RIGHT, text_color=Color('lightblue'))
        self._fps_counter.enabled = config.world.show_debug_info
        self.append_child(self._fps_counter)

    def draw(self, screen: Surface):
        self.draw_textures(screen)
        self.draw_health_bars(screen)
        self.draw_construction_bars(screen)
        self.draw_nicks(screen)

        if config.world.show_debug_info:
            self.draw_debug(screen)

    def draw_nicks(self, screen: Surface):
        for _, (_, position, owner) in self._ecs.get_entities_with_components((CoreBuildingComponent,
                                                                               PositionComponent,
                                                                               PlayerOwnerComponent)):
            text_image = self._nicks_font.render(self._players[owner.socket_id].nick, True,
                                                 color_name_to_pygame_color[owner.color_name])
            center = position.position_according_to_camera(self._camera)
            screen.blit(text_image, text_image.get_rect(center=(center[0], center[1] - 100)))

    def draw_textures(self, screen: Surface):
        for _, (texture, position) in self._ecs.get_entities_with_components((TextureComponent, PositionComponent)):
            texture.blit(screen, position.position_according_to_camera(self._camera))

    def draw_health_bars(self, screen: Surface):
        for _, (texture, health, position) in self._ecs.get_entities_with_components(
                (TextureComponent, HealthComponent, PositionComponent)):
            if health.amount == health.max_amount:
                continue
            health_rect = Rect(0, 0, 50, 5)
            health_rect.center = position.position_according_to_camera(self._camera)
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width = health_rect.width * health.amount / health.max_amount
            pygame.draw.rect(screen, Color('red'), health_rect)

    def draw_construction_bars(self, screen: Surface):
        for _, (texture, uncompleted_building, position) in self._ecs.get_entities_with_components(
                (TextureComponent, UncompletedBuildingComponent, PositionComponent)):
            health_rect = Rect(0, 0, 50, 5)
            health_rect.center = position.position_according_to_camera(self._camera)
            health_rect.move_ip(0, -5)
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width = health_rect.width * uncompleted_building.progress / uncompleted_building.required_progress
            pygame.draw.rect(screen, Color('yellow'), health_rect)

    def draw_debug(self, screen: Surface):
        for _, (collider, position) in self._ecs.get_entities_with_components(
                (ColliderComponent, PositionComponent)):
            pygame.draw.circle(screen, Color('green') if collider.static else Color('lightgreen'),
                               position.position_according_to_camera(self._camera), collider.radius, 1)

    def on_key_up(self, key: int, unicode: str, mod: int, scancode: int) -> bool | None:
        if key == pygame.K_F3:
            config.world.show_debug_info = not config.world.show_debug_info
            self._fps_counter.enabled = config.world.show_debug_info
            upload_config_to_disc()

            return True
