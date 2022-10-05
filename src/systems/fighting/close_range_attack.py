from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.chase import ChaseComponent
from src.components.fighting.close_range_attack import CloseRangeAttackComponent
from src.components.fighting.health import HealthComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender
from src.utils.collision import is_close_to_target


def close_range_attack_system(entity_id: EntityId,
                              close_range_attack: CloseRangeAttackComponent,
                              owner: PlayerOwnerComponent,
                              position: PositionComponent,
                              ecs: EntityComponentSystem,
                              chase: ChaseComponent,
                              collider: ColliderComponent,
                              action_sender: ServerActionSender):
    if chase.entity_id is None:
        return

    if not is_close_to_target(ecs, chase, collider, position):
        return

    if close_range_attack.current_delay < close_range_attack.delay:
        close_range_attack.current_delay += 1
        return

    close_range_attack.current_delay = 0

    enemy_health, = ecs.get_components(chase.entity_id, (HealthComponent,))

    enemy_health.apply_damage(close_range_attack.damage)
    action_sender.update_component_info(chase.entity_id, enemy_health)
    action_sender.show_popup(str(close_range_attack.damage), chase.chase_position, 'red')

