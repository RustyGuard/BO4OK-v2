import random

from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.unit_production import UnitProductionComponent
from src.entities import unit_production_factories
from src.entity_component_system import EntityComponentSystem


def unit_production_system(unit_prod: UnitProductionComponent, position: PositionComponent, ecs: EntityComponentSystem,
                           player_owner: PlayerOwnerComponent):
    if not unit_prod.unit_queue:
        return

    unit_prod.current_delay += 1
    if unit_prod.current_delay >= unit_prod.delay:
        unit_prod.current_delay = 0
        unit_to_produce = unit_prod.unit_queue.pop(0)
        entity = unit_production_factories[unit_to_produce](x=position.x + random.randint(-150, 150),
                                                            y=position.y + random.randint(-150, 150),
                                                            player_owner=player_owner)
        ecs.create_entity(entity)
