from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_mine(x: float, y: float):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/mine/mine.png'),
    ]
