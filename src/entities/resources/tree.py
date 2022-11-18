from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.worker.resource import ResourceComponent


def create_tree(x: float, y: float):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/tree/tree.png'),
        ResourceComponent(wood=50),
    ]
