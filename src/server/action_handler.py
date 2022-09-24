from typing import Any

from src.components.chase import ChaseComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.unit_production import UnitProductionComponent
from src.constants import ServerCommands
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.entities import buildings, building_factories
from src.server.action_sender import ServerActionSender
from src.utils.math_utils import spread_position


class ServerActionHandler:
    def __init__(self, ecs: EntityComponentSystem, players: dict[int, PlayerInfo], action_sender: ServerActionSender):
        self.ecs = ecs
        self.players = players
        self.action_sender = action_sender

    def handle_action(self, command: str, args: list[Any], socket_id: int):
        if command == ServerCommands.PRODUCE_UNIT:
            self.handle_produce(socket_id, args[0], args[1])
        elif command == ServerCommands.PLACE_UNIT:
            self.handle_place(socket_id, args[0], args[1], args[2])
        elif command == ServerCommands.SET_TARGET_MOVE:
            self.handle_force_move(socket_id, args[0], tuple(args[1]))

        else:
            print(f'Unknown command: {command}({args})')

    def handle_produce(self, socket_id: int, build_entity_id: EntityId, unit_name: str):
        player = self.players[socket_id]
        components = self.ecs.get_components(build_entity_id, (UnitProductionComponent, PlayerOwnerComponent))
        if components is None:
            print(f'This entity({build_entity_id=}) can not produce anything, you are stupid, {socket_id=}')
            return

        producing_component, owner_component = components
        if owner_component.socket_id != socket_id:
            print(f'''{socket_id=} trying to produce units in other's({owner_component.socket_id}) building''')
            return

        if producing_component.add_to_queue(unit_name, player):
            self.action_sender.update_resource_info(player)

    def handle_place(self, socket_id: int, build_name: str, position_x: float, position_y: float):
        player = self.players[socket_id]

        cost = buildings[build_name]
        if not player.has_enough(cost):
            return

        self.ecs.create_entity(building_factories[build_name](
            x=position_x,
            y=position_y,
            player_owner=PlayerOwnerComponent(
                socket_id=player.socket_id,
                color_name=player.color_name,
                nick=player.nick,
            )
        ))
        player.spend(cost)
        self.action_sender.update_resource_info(player)

    def handle_force_move(self, socket_id: int, entities: list[EntityId], position: tuple[float, float]):
        for entity_id in entities:
            components = self.ecs.get_components(entity_id, (ChaseComponent, PlayerOwnerComponent))
            if components is None:
                print(f'This entity({entity_id=}) can not chase anything, you are stupid, {socket_id=}')
                return
            chase, owner_component = components

            if owner_component.socket_id != socket_id:
                print(f'''{socket_id=} trying to force to move {entity_id=} in other's({owner_component.socket_id}) team''')
                return

            chase.chase_position = PositionComponent(*spread_position(position, 50))
            chase.entity_id = None

            self.action_sender.update_component_info(entity_id, chase)

