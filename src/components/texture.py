from dataclasses import dataclass

import pygame
from pygame.surface import Surface

from src.utils.image import get_image
from src.utils.math_utils import convert_to_main_angle


@dataclass(slots=True)
class TextureComponent:
    texture_path: str
    rotation_angle: int = 0

    @classmethod
    def create_from_filepath(cls, texture_path: str, rotation_angle: int = 0):
        return cls(
            texture_path=texture_path,
            rotation_angle=convert_to_main_angle(rotation_angle),
        )

    @property
    def texture(self) -> pygame.Surface:
        return get_image(self.texture_path)

    def blit(self, surface: Surface, position: tuple[float, float]):
        texture = self.texture

        rotated_image = pygame.transform.rotate(texture, self.rotation_angle)
        new_rect = rotated_image.get_rect(center=position)

        surface.blit(rotated_image, new_rect)
