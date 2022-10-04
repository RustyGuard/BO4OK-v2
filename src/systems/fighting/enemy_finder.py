from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.chase import ChaseComponent
from src.components.fighting.enemy_finder import EnemyFinderComponent
from src.components.fighting.health import HealthComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender

DELAY_BETWEEN_ATTEMPTS = 60


def enemy_finder_system(entity_id: EntityId, ecs: EntityComponentSystem, action_sender: ServerActionSender,
                        position: PositionComponent,
                        owner: PlayerOwnerComponent,
                        chase: ChaseComponent,
                        enemy_finder: EnemyFinderComponent
                        ):
    if enemy_finder.delay > 0:
        enemy_finder.delay -= 1
        return

    if chase.chase_position is not None:
        return

    nearest = min(
        ((other_entity_id, (other_position, other_owner))
         for other_entity_id, (other_position, other_owner, _) in
         ecs.get_entities_with_components((PositionComponent,
                                           PlayerOwnerComponent,
                                           HealthComponent))
         if owner.socket_id != other_owner.socket_id),
        key=lambda entity: position.distance(entity[1][0]),
        default=None)
    if nearest is None:
        return

    other_entity_id, (other_position, other_owner) = nearest

    if other_position.distance(position) > enemy_finder.anger_range:
        enemy_finder.delay = DELAY_BETWEEN_ATTEMPTS
        return

    chase.entity_id = other_entity_id
    chase.chase_position = other_position
    action_sender.update_component_info(entity_id, chase)
