import dataclasses
from multiprocessing.connection import Connection
from typing import Any

from src.constants import ClientCommands
from src.core.types import PlayerInfo
from src.core.entity_component_system import Component, EntityId


class ServerActionSender:
    def __init__(self, write_action_connection: Connection):
        self.write_action_connection = write_action_connection

    def send(self, command: list[Any], player_id: int | None = None) -> None:
        """Если player_id не указан - будет отправлено всем"""
        if player_id == -1:
            return
        self.write_action_connection.send((command, player_id))

    def send_entity(self, entity_id: EntityId, components: list[Component]) -> None:
        """Оправить сущность для её появления у игроков"""
        self.send([ClientCommands.CREATE, {
            'entity_id': entity_id,
            'components': [
                dataclasses.asdict(component) | {'component_class': component.__class__.__name__}
                for component in components]
        }])

    def sync_entity(self, entity_id: EntityId, components: list[Component]) -> None:
        """Синхронизовать сущность у игроков"""
        self.send([ClientCommands.UPDATE, {
            'entity_id': entity_id,
            'components': [
                dataclasses.asdict(component)
                for component in components]
        }])

    def update_resource_info(self, player: PlayerInfo) -> None:
        self.send([ClientCommands.RESOURCE_INFO, player.resources.dict()], player.socket_id)

    def update_component_info(self, entity_id: EntityId, component: Component) -> None:
        self.send([ClientCommands.COMPONENT_INFO,
                   entity_id, component.__class__.__name__, dataclasses.asdict(component)])

    def remove_entity(self, entity_id: EntityId):
        self.send([ClientCommands.DEAD, entity_id])