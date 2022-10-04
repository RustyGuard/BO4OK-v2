from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent


def create_tree(x: float, y: float):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/icon/tree.png'),
    ]
