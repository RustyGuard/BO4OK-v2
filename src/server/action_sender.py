import dataclasses
from multiprocessing.connection import Connection
from typing import Any

from src.components.base.position import PositionComponent
from src.constants import ClientCommands, SoundCode
from src.core.camera import Camera
from src.core.types import Component, EntityId
from src.core.types import PlayerInfo
from src.sound_player import play_sound
from src.utils.sound_volume import get_sound_volume_from_distance


class ServerActionSender:
    def __init__(self, write_action_connection: Connection, camera: Camera):
        self.write_action_connection = write_action_connection
        self.camera = camera

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

    def show_popup(self, label: str, position: PositionComponent, color: str):
        self.send([ClientCommands.POPUP, label, position.x, position.y, color])

    def play_sound(self, sound: SoundCode, sound_position: tuple[float, float] = None):
        self.send([ClientCommands.SOUND, sound.name, sound_position])

        volume = 1
        if sound_position is not None:
            distance = self.camera.distance_to(sound_position)
            volume = get_sound_volume_from_distance(distance)
            if volume <= 10 ** -3:
                return
        play_sound(sound, volume)

