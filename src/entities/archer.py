from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_archer(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/archer/{player_owner.color_name}.png'),

    ]
