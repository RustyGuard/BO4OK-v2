from dataclasses import dataclass

from src.core.camera import Camera


@dataclass(slots=True)
class PositionComponent:
    x: float
    y: float

    def to_tuple(self):
        return self.x, self.y

    def position_according_to_camera(self, camera: Camera):
        return self.x + camera.offset_x, self.y + camera.offset_y
