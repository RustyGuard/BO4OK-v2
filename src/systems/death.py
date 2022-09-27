from src.components.chase import ChaseComponent
from src.components.health import HealthComponent
from src.components.meat import ReturnMeatOnDeath, MaxMeatIncrease
from src.components.player_owner import PlayerOwnerComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId, PlayerInfo
from src.server.action_sender import ServerActionSender


def bring_meat_back(entity_id: EntityId, action_sender: ServerActionSender,
                    ecs: EntityComponentSystem, players: dict[int, PlayerInfo]):
    owner = ecs.get_component(entity_id, PlayerOwnerComponent)
    if owner is None:
        return
    owner_info = players[owner.socket_id]
    resources_changed = False

    meat_on_death = ecs.get_component(entity_id, ReturnMeatOnDeath)
    if meat_on_death:
        owner_info.resources.meat -= meat_on_death.meat_amount
        resources_changed = True

    max_meat_increase = ecs.get_component(entity_id, MaxMeatIncrease)
    if max_meat_increase:
        owner_info.resources.max_meat -= max_meat_increase.meat_amount
        resources_changed = True

    if resources_changed:
        action_sender.update_resource_info(owner_info)


def death_system(entity_id: EntityId, health: HealthComponent, action_sender: ServerActionSender,
                 ecs: EntityComponentSystem, players: dict[int, PlayerInfo]):
    if health.amount > 0:
        return

    for angry_entity_id, (chase,) in ecs.get_entities_with_components((ChaseComponent,)):
        if chase.entity_id != entity_id:
            continue

        chase.entity_id = None
        chase.chase_position = None
        action_sender.update_component_info(angry_entity_id, chase)

    bring_meat_back(entity_id, action_sender, ecs, players)

    ecs.remove_entity(entity_id)
