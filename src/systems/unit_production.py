import random

from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.meat import ReturnMeatOnDeathComponent
from src.components.unit_production import UnitProductionComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.entities import unit_production_factories
from src.server.action_sender import ServerActionSender


def unit_production_system(entity_id: EntityId, unit_prod: UnitProductionComponent, position: PositionComponent, ecs: EntityComponentSystem,
                           player_owner: PlayerOwnerComponent, action_sender: ServerActionSender):
    if not unit_prod.unit_queue:
        return

    if unit_prod.current_delay < unit_prod.delay:
        unit_prod.current_delay += 1
        return

    unit_prod.current_delay = 0
    unit_to_produce = unit_prod.unit_queue.pop(0)
    entity = unit_production_factories[unit_to_produce](x=position.x + random.randint(-150, 150),
                                                        y=position.y + random.randint(-150, 150),
                                                        player_owner=player_owner)
    entity.append(ReturnMeatOnDeathComponent(unit_prod.producible_units[unit_to_produce].meat))
    action_sender.update_component_info(entity_id, unit_prod)
    ecs.create_entity(entity)
    print(entity)
