from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent


def create_fortress(x: float, y: float, player_color_name: str, player_nick: str, player_socket_id: int):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/fortress/{player_color_name}.png'),
        MinimapIconComponent('square', player_color_name),
        PlayerOwnerComponent(player_color_name, player_nick, player_socket_id),
        UnitProductionComponent(delay=180),
    ]
