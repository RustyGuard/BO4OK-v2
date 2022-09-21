from src.components.position import PositionComponent
from src.components.velocity import VelocityComponent


def velocity_system(velocity: VelocityComponent, position: PositionComponent):
    position.x += velocity.speed_x
    position.y += velocity.speed_y
