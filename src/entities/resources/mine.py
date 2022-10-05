from src.components.base.collider import ColliderComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.worker.resource import ResourceComponent


def create_mine(x: float, y: float):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/mine/mine.png'),
        ResourceComponent(money=5000),
        ColliderComponent(radius=50, static=True),
    ]
