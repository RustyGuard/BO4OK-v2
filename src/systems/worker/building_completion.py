from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.constants import SoundCode
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.entities import building_factories
from src.server.action_sender import ServerActionSender


def building_completion_system(entity_id: EntityId,
                               uncompleted_building: UncompletedBuildingComponent,
                               owner: PlayerOwnerComponent,
                               position: PositionComponent,
                               ecs: EntityComponentSystem,
                               action_sender: ServerActionSender):
    if uncompleted_building.progress < uncompleted_building.required_progress:
        return

    ecs.remove_entity(entity_id)
    ecs.create_entity(building_factories[uncompleted_building.build_name](
        x=position.x,
        y=position.y,
        player_owner=owner,
    ))
    action_sender.play_sound(SoundCode.CONSTRUCTION_COMPLETED)

