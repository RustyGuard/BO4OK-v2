from src.components.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.core.types import RequiredCost


def create_casern(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        TextureComponent.create_from_filepath(f'assets/building/casern/{player_owner.color_name}.png'),
        MinimapIconComponent('circle', player_owner.color_name),
        player_owner,
        UnitProductionComponent(delay=60, producible_units={'archer': RequiredCost(money=1, wood=5, meat=1),
                                                            'warrior': RequiredCost(money=2, meat=2)}),
        HealthComponent(max_amount=300),
    ]
