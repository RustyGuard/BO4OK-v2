import pygame
from pygame.event import Event

from src.config import config
from src.constants import EVENT_UPDATE
from src.core.camera import Camera
from src.ui import UIElement


class CameraInputHandler(UIElement):
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera

    def update(self, event: Event):
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

            self.camera.move(x_change, y_change)

            if x_change != 0 or y_change != 0:
                self.camera.increase_speed()
            else:
                self.camera.decrease_speed()

