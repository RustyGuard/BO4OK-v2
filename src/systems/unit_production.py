import random

from src.components.meat import ReturnMeatOnDeath
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.unit_production import UnitProductionComponent
from src.core.entity_component_system import EntityComponentSystem
from src.entities import unit_production_factories


def unit_production_system(unit_prod: UnitProductionComponent, position: PositionComponent, ecs: EntityComponentSystem,
                           player_owner: PlayerOwnerComponent):
    if not unit_prod.unit_queue:
        return

    if unit_prod.current_delay < unit_prod.delay:
        unit_prod.current_delay += 1

    unit_prod.current_delay = 0
    unit_to_produce = unit_prod.unit_queue.pop(0)
    entity = unit_production_factories[unit_to_produce](x=position.x + random.randint(-150, 150),
                                                        y=position.y + random.randint(-150, 150),
                                                        player_owner=player_owner)
    entity.append(ReturnMeatOnDeath(unit_prod.producible_units[unit_to_produce].meat))
    ecs.create_entity(entity)
    print(entity)
