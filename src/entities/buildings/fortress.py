from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.core_building import CoreBuildingComponent
from src.components.fighting.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.unit_production import UnitProductionComponent
from src.components.worker.depot import ResourceDepotComponent
from src.core.types import RequiredCost


def create_fortress(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/fortress/{player_owner.color_name}.png'),
        MinimapIconComponent('square', player_owner.color_name, icon_size=15, icon_border=True),
        player_owner,
        UnitProductionComponent(delay=3 * 60,
                                producible_units={'worker': RequiredCost(money=1, wood=1, meat=1)}),
        HealthComponent(max_amount=1000),
        ResourceDepotComponent(),
        ColliderComponent(radius=75, static=True),
        CoreBuildingComponent(),
    ]
