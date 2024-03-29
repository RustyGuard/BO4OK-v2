from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent, MarkShape
from src.components.unit_production import UnitProductionComponent
from src.core.types import RequiredCost


def create_workshop(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/workshop/{player_owner.color_name}.png'),
        MinimapIconComponent(MarkShape.CIRCLE, player_owner.color_name),
        player_owner,
        UnitProductionComponent(delay=15 * 60, producible_units={'ballista': RequiredCost(money=100, wood=500, meat=2)}),
        HealthComponent(max_amount=500),
        ColliderComponent(radius=60, static=True),
    ]
