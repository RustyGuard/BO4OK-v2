from typing import Any

from src.components.player_owner import PlayerOwnerComponent
from src.components.unit_production import UnitProductionComponent
from src.constants import ServerCommands
from src.core.types import PlayerInfo
from src.entity_component_system import EntityComponentSystem, EntityId
from src.server.action_sender import ServerActionSender


class ServerActionHandler:
    def __init__(self, ecs: EntityComponentSystem, players: dict[int, PlayerInfo], action_sender: ServerActionSender):
        self.ecs = ecs
        self.players = players
        self.action_sender = action_sender

    def handle_action(self, command: str, args: list[Any], socket_id: int):
        if command == ServerCommands.PRODUCE_UNIT:
            self.handle_produce(socket_id, args[0], args[1])
        else:
            print(f'Unknown command: {command}({args})')

    def handle_produce(self, socket_id: int, build_entity_id: EntityId, unit_name: str):
        player = self.players[socket_id]
        components = self.ecs.get_components(build_entity_id, [UnitProductionComponent, PlayerOwnerComponent])
        if components is None:
            print(f'This entity({build_entity_id=}) can not produce anything, you are stupid, {socket_id=}')
            return

        producing_component, owner_component = components
        if owner_component.socket_id != socket_id:
            print(f'''{socket_id=} trying to produce units in other's({owner_component.socket_id}) building''')

        if producing_component.add_to_queue(unit_name, player):
            self.action_sender.update_resource_info(player)


