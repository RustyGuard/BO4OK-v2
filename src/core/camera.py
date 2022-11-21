import math

import pygame

from src.config import config
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo


class Camera:
    def __init__(self):
        self.offset_x = config.screen.size[0] / 2
        self.offset_y = config.screen.size[1] / 2
        self.speed = 1
        self.initial_position_set = False

    def move(self, x, y):
        self.offset_x += x * self.speed
        self.offset_y += y * self.speed
        self.validate_position()

    def increase_speed(self):
        self.speed += config.camera.step_faster
        self.speed = min(config.camera.max_speed, self.speed)

    def decrease_speed(self):
        self.speed -= config.camera.step_slower
        self.speed = max(config.camera.min_speed, self.speed)

    def validate_position(self):
        world_size = config.world.size
        if self.offset_x < -world_size + config.screen.size[0]:
            self.offset_x = -world_size + config.screen.size[0]
        if self.offset_x > world_size:
            self.offset_x = world_size
        if self.offset_y < -world_size + config.screen.size[1]:
            self.offset_y = -world_size + config.screen.size[1]
        if self.offset_y > world_size:
            self.offset_y = world_size

    def set_center(self, center: tuple[float, float]):
        self.offset_x, self.offset_y = center[0] + config.screen.size[0] / 2, center[1] + config.screen.size[1] / 2
        self.validate_position()

    def get_in_game_mouse_position(self) -> tuple[float, float]:
        mouse_pos = pygame.mouse.get_pos()
        return mouse_pos[0] - self.offset_x, mouse_pos[1] - self.offset_y

    def to_screen_position(self, pos: tuple[float, float]):
        return pos[0] + self.offset_x, pos[1] + self.offset_y

    def distance_to(self, position: tuple[float, float]):
        return math.sqrt((position[0] + self.offset_x - config.screen.width / 2) ** 2 + (
                position[1] + self.offset_y - config.screen.height / 2) ** 2)

    def check_if_fortress_appeared(self, ecs: EntityComponentSystem, player_owner: PlayerInfo):
        if self.initial_position_set:
            return
        from src.components.base.player_owner import PlayerOwnerComponent
        from src.components.base.position import PositionComponent
        from src.components.core_building import CoreBuildingComponent

        for _, (_, position, owner) in ecs.get_entities_with_components((CoreBuildingComponent,
                                                                    PositionComponent,
                                                                    PlayerOwnerComponent)):
            if owner.socket_id == player_owner.socket_id:
                self.set_center((-position.x, -position.y))
                self.initial_position_set = True
