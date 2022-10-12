import pygame
from pygame import Color
from pygame.font import Font
from pygame.sprite import Sprite, Group

from src.components.base.position import PositionComponent
from src.constants import EVENT_UPDATE
from src.core.camera import Camera
from src.ui import UIElement
from src.utils.math_utils import spread_position


class DamageIndicator(Sprite):
    def __init__(self, label: str, position: tuple[float, float], font: Font, color: Color):
        super().__init__()

        self.image = font.render(label, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.frames_left = 20

    def update(self, event: pygame.event.Event) -> None:
        if event.type == EVENT_UPDATE:
            self.frames_left -= 1
            self.rect.move_ip(0, -1)
            if self.frames_left <= 0:
                self.kill()


class DamageIndicators(UIElement):
    def __init__(self, camera: Camera):
        super().__init__()
        self.indicators = Group()
        self.font = pygame.font.SysFont('Comic Sans MS', 20)
        self.camera = camera

    def show_indicator(self, label: str, position: PositionComponent, color: str):
        self.indicators.add(
            DamageIndicator(label, spread_position(position.position_according_to_camera(self.camera), 10), self.font,
                            Color(color)))

    def draw(self, screen):
        self.indicators.draw(screen)

    def update(self, event):
        self.indicators.update(event)