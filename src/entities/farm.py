from src.components.health import HealthComponent
from src.components.meat import MaxMeatIncrease
from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_farm(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/farm/{player_owner.color_name}.png'),
        MinimapIconComponent('square', player_owner.color_name),
        player_owner,
        HealthComponent(max_amount=500),
        MaxMeatIncrease(20),
    ]