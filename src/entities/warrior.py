from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_warrior(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/warrior/{player_owner.color_name}.png'),

    ]
