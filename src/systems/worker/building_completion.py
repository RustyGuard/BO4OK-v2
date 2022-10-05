from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.entities import building_factories


def building_completion_system(entity_id: EntityId,
                               uncompleted_building: UncompletedBuildingComponent,
                               owner: PlayerOwnerComponent,
                               position: PositionComponent,
                               ecs: EntityComponentSystem):
    if uncompleted_building.progress < uncompleted_building.required_progress:
        return

    ecs.remove_entity(entity_id)
    ecs.create_entity(building_factories[uncompleted_building.build_name](
        x=position.x,
        y=position.y,
        player_owner=owner,
    ))
