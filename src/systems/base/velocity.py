from src.components.base.position import PositionComponent
from src.components.base.velocity import VelocityComponent


def velocity_system(velocity: VelocityComponent, position: PositionComponent):
    position.x += velocity.speed_x
    position.y += velocity.speed_y
