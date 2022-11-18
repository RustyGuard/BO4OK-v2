from typing import Any, Callable

from src.constants import ClientCommands, SoundCode
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.sound_player import play_sound
from src.utils.sound_volume import get_sound_volume_from_distance


class ClientActionHandler:
    def __init__(self, ecs: EntityComponentSystem, current_player: PlayerInfo, camera: Camera):
        self.ecs = ecs
        self.current_player = current_player
        self.camera = camera
        self.hooks = {}

    def add_hook(self, command_id: int, hook: Callable[..., Any]):
        self.hooks[command_id] = hook

    def handle_action(self, command: str, args: list[Any]):
        if command == ClientCommands.CREATE:
            self.handle_create(args[0])

        elif command == ClientCommands.DEAD:
            self.handle_remove(args[0])

        elif command == ClientCommands.RESOURCE_INFO:
            self.handle_player_info_update(args[0])

        elif command == ClientCommands.COMPONENT_INFO:
            self.handle_update_component_info(args[0], args[1], args[2])

        elif command == ClientCommands.SOUND:
            self.handle_play_sound(args[0], args[1])

        elif command not in self.hooks:
            print(f'Unknown command: {command}({args})')

        hook = self.hooks.get(command, None)
        if hook:
            hook(*args)

    def handle_create(self, entity_json: dict):
        entity_id = entity_json['entity_id']
        components = []
        for component_json in entity_json['components']:
            component_class_name = component_json.pop('component_class')
            component_class = next(component_class for component_class in self.ecs.components if
                                   component_class.__name__ == component_class_name)
            component = component_class(**component_json)
            if hasattr(component, 'assemble_on_client'):
                component.assemble_on_client(self.ecs)
            components.append(component)
        self.ecs.create_entity(components, entity_id)

    def handle_remove(self, entity_id: EntityId):
        self.ecs.remove_entity(entity_id)

    def handle_player_info_update(self, player_info_json):
        for field, value in player_info_json.items():
            setattr(self.current_player.resources, field, value)

    def handle_update_component_info(self, entity_id: EntityId, component_class_name: str, component_json):
        component_class = next(component_class for component_class in self.ecs.components if
                               component_class.__name__ == component_class_name)
        component = component_class(**component_json)
        if hasattr(component, 'assemble_on_client'):
            component.assemble_on_client(self.ecs)
        self.ecs.components[component_class][entity_id] = component

    def handle_play_sound(self, sound_name: str, sound_position: tuple[float, float] | None):
        volume = 1
        if sound_position is not None:
            distance = self.camera.distance_to(sound_position)
            volume = get_sound_volume_from_distance(distance)
            if volume <= 10 ** -3:
                return
        sound = SoundCode[sound_name]
        play_sound(sound, volume)
