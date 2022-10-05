from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.chase import ChaseComponent
from src.components.worker.resource import ResourceComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.components.worker.work_finder import WorkFinderComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender

DELAY_BETWEEN_ATTEMPTS = 60


def work_finder_system(entity_id: EntityId, ecs: EntityComponentSystem,
                       action_sender: ServerActionSender,
                       position: PositionComponent,
                       chase: ChaseComponent,
                       enemy_finder: WorkFinderComponent,
                       owner: PlayerOwnerComponent,
                       ):
    if enemy_finder.delay > 0:
        enemy_finder.delay -= 1
        return

    if chase.chase_position is not None:
        return

    nearest_uncompleted_building = min(
        ((building_entity_id, (building_position,))
         for building_entity_id, (building_position, building_progress, building_owner) in
         ecs.get_entities_with_components((PositionComponent,
                                           UncompletedBuildingComponent,
                                           PlayerOwnerComponent))
         if building_owner.socket_id == owner.socket_id and building_progress.progress < building_progress.required_progress),
        key=lambda entity: position.distance(entity[1][0]),
        default=None)
    if nearest_uncompleted_building is not None:
        (building_entity_id, (building_position,)) = nearest_uncompleted_building

        chase.entity_id = building_entity_id
        chase.chase_position = building_position
        action_sender.update_component_info(entity_id, chase)

        return

    nearest_resource = min(
        ((other_entity_id, (other_position,))
         for other_entity_id, (other_position, _) in
         ecs.get_entities_with_components((PositionComponent,
                                           ResourceComponent))),
        key=lambda entity: position.distance(entity[1][0]),
        default=None)
    if nearest_resource is None:
        return

    other_entity_id, (other_position,) = nearest_resource

    chase.entity_id = other_entity_id
    chase.chase_position = other_position
    action_sender.update_component_info(entity_id, chase)
