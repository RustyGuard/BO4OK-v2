from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.chase import ChaseComponent
from src.components.worker.depot import ResourceDepotComponent
from src.components.worker.resource import ResourceComponent
from src.components.worker.resource_gatherer import ResourceGathererComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId, PlayerInfo
from src.server.action_sender import ServerActionSender
from src.utils.collision import is_close_to_target


def working_system(entity_id: EntityId,
                   resource_gatherer: ResourceGathererComponent,
                   owner: PlayerOwnerComponent,
                   players: list[PlayerInfo],
                   collider: ColliderComponent,
                   position: PositionComponent,
                   ecs: EntityComponentSystem,
                   chase: ChaseComponent,
                   action_sender: ServerActionSender):
    if chase.entity_id is None:
        return

    if not is_close_to_target(ecs, chase, collider, position):
        return

    if resource_gatherer.current_delay < resource_gatherer.delay:
        resource_gatherer.current_delay += 1
        return

    resource_gatherer.current_delay = 0

    uncompleted_building = ecs.get_component(chase.entity_id, UncompletedBuildingComponent)
    resource_source = ecs.get_component(chase.entity_id, ResourceComponent)
    resource_depot = ecs.get_component(chase.entity_id, ResourceDepotComponent)

    if uncompleted_building is not None:
        uncompleted_building.progress += 1
        action_sender.update_component_info(chase.entity_id, uncompleted_building)

        if uncompleted_building.progress >= uncompleted_building.required_progress:
            chase.drop_target()

    elif resource_source is not None:
        taken_wood = min(resource_gatherer.gathering_speed, resource_source.wood)
        resource_source.wood -= taken_wood
        resource_gatherer.wood_carried += taken_wood
        if taken_wood:
            action_sender.show_popup(str(taken_wood), chase.chase_position, 'brown')

        taken_money = min(resource_gatherer.gathering_speed, resource_source.money)
        resource_source.money -= taken_money
        resource_gatherer.money_carried += taken_money
        if taken_money:
            action_sender.show_popup(str(taken_money), chase.chase_position, 'yellow')

        if resource_source.money == 0 and resource_source.wood == 0:
            ecs.remove_entity(chase.entity_id)
            chase.drop_target()

        if resource_gatherer.is_backpack_full:
            nearest_depot = min(
                ((other_entity_id, (other_position,))
                 for other_entity_id, (other_position, other_owner, _) in
                 ecs.get_entities_with_components((PositionComponent,
                                                   PlayerOwnerComponent,
                                                   ResourceDepotComponent)
                                                  )
                 if owner.socket_id == other_owner.socket_id),
                key=lambda entity: position.distance(entity[1][0]),
                default=None)

            if not nearest_depot:
                print('No depots!!!')
                return

            depot_entity_id, (depot_position,) = nearest_depot
            chase.entity_id = depot_entity_id
            chase.chase_position = depot_position
            action_sender.update_component_info(entity_id, chase)

        return

    elif resource_depot is not None:
        player = players[owner.socket_id]

        if resource_gatherer.wood_carried:
            player.resources.wood += resource_gatherer.wood_carried
            action_sender.show_popup(f'+{resource_gatherer.wood_carried}', chase.chase_position, 'brown')
            resource_gatherer.wood_carried = 0

        if resource_gatherer.money_carried:
            player.resources.money += resource_gatherer.money_carried
            action_sender.show_popup(f'+{resource_gatherer.money_carried}', chase.chase_position, 'yellow')
            resource_gatherer.money_carried = 0

        action_sender.update_resource_info(player)

        chase.drop_target()
    else:
        chase.drop_target()
