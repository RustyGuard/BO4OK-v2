from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.worker.depot import ResourceDepotComponent


def create_fortress(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/fortress/{player_owner.color_name}.png'),
        MinimapIconComponent('square', player_owner.color_name),
        player_owner,
        HealthComponent(max_amount=1000),
        ResourceDepotComponent(),
    ]
