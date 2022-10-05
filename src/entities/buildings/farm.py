from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.health import HealthComponent
from src.components.meat import MaxMeatIncreaseComponent
from src.components.minimap_icon import MinimapIconComponent


def create_farm(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/farm/{player_owner.color_name}.png'),
        MinimapIconComponent('square', player_owner.color_name),
        player_owner,
        HealthComponent(max_amount=500),
        MaxMeatIncreaseComponent(20),
        ColliderComponent(radius=25, static=True),
    ]
