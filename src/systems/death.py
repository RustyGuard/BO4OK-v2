from src.components.chase import ChaseComponent
from src.components.health import HealthComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender


def death_system(entity_id: EntityId, health: HealthComponent, action_sender: ServerActionSender, ecs: EntityComponentSystem):
    if health.amount == 0:
        ecs.remove_entity(entity_id)
        for angry_entity_id, (chase,) in ecs.get_entities_with_components((ChaseComponent,)):
            if chase.entity_id != entity_id:
                continue

            chase.entity_id = None
            chase.chase_position = None
            action_sender.update_component_info(angry_entity_id, chase)
