import pygame

from src.config import config
from src.constants import EVENT_UPDATE


class Camera:
    def __init__(self):
        self.offset_x = config.screen.size[0] / 2
        self.offset_y = config.screen.size[1] / 2
        self.speed = 1

    def update(self, event):
        if event.type == EVENT_UPDATE:
            keys = pygame.key.get_pressed()
            x_change, y_change = 0, 0
            if keys[pygame.K_d]:
                x_change -= 1
            if keys[pygame.K_a]:
                x_change += 1
            if keys[pygame.K_s]:
                y_change -= 1
            if keys[pygame.K_w]:
                y_change += 1
            self.move(x_change, y_change)
            if x_change != 0 or y_change != 0:
                self.speed += config.camera.step_faster
                self.speed = min(config.camera.max_speed, self.speed)
            else:
                self.speed -= config.camera.step_slower
                self.speed = max(config.camera.min_speed, self.speed)

    def move(self, x, y):
        self.offset_x += x * self.speed
        self.offset_y += y * self.speed
        self.validate_position()

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
