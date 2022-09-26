from src.components.chase import ChaseComponent
from src.components.close_range_attack import CloseRangeAttack
from src.components.health import HealthComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender


def close_range_attack_system(entity_id: EntityId,
                              close_range_attack: CloseRangeAttack,
                              owner: PlayerOwnerComponent,
                              position: PositionComponent,
                              ecs: EntityComponentSystem,
                              chase: ChaseComponent,
                              action_sender: ServerActionSender):
    if chase.entity_id is None:
        return

    if chase.chase_position.distance(position) > chase.distance_until_attack:
        return

    close_range_attack.current_delay += 1
    if close_range_attack.current_delay >= close_range_attack.delay:
        close_range_attack.current_delay = 0

        enemy_health, = ecs.get_components(chase.entity_id, (HealthComponent,))

        enemy_health.apply_damage(close_range_attack.damage)
        action_sender.update_component_info(chase.entity_id, enemy_health)
