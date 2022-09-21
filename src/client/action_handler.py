from typing import Any

from src.constants import ClientCommands
from src.entity_component_system import EntityComponentSystem, EntityId


class ClientActionHandler:
    def __init__(self, ecs: EntityComponentSystem):
        self.ecs = ecs

    def handle_action(self, command: str, args: list[Any]):
        if command == ClientCommands.CREATE:
            self.handle_create(args[0])

        elif command == ClientCommands.DEAD:
            self.handle_remove(args[0])

    def handle_create(self, entity_json: dict):
        entity_id = entity_json['entity_id']
        components = []
        for component_json in entity_json['components']:
            component_class_name = component_json.pop('component_class')
            component_class = next(component_class for component_class in self.ecs.components if
                                   component_class.__name__ == component_class_name)
            components.append(component_class(**component_json))
        self.ecs.create_entity(components, entity_id)

    def handle_remove(self, entity_id: EntityId):
        self.ecs.remove_entity(entity_id)
