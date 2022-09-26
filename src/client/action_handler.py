from typing import Any

from src.components.position import PositionComponent
from src.constants import ClientCommands
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.menus.damage_indicators import DamageIndicators


class ClientActionHandler:
    def __init__(self, ecs: EntityComponentSystem, current_player: PlayerInfo, damage_indicators: DamageIndicators):
        self.ecs = ecs
        self.current_player = current_player
        self.damage_indicators = damage_indicators

    def handle_action(self, command: str, args: list[Any]):
        if command == ClientCommands.CREATE:
            self.handle_create(args[0])

        elif command == ClientCommands.DEAD:
            self.handle_remove(args[0])

        elif command == ClientCommands.RESOURCE_INFO:
            self.handle_player_info_update(args[0])

        elif command == ClientCommands.COMPONENT_INFO:
            self.handle_update_component_info(args[0], args[1], args[2])

        elif command == ClientCommands.DAMAGE:
            self.handle_damage(args[0], args[1], args[2])

        else:
            print(f'Unknown command: {command}({args})')

    def handle_damage(self, enemy_id: EntityId, victim_id: EntityId, damage: int):
        position = self.ecs.get_component(victim_id, PositionComponent)
        if position is None:
            return
        self.damage_indicators.show_indicator(damage, position)

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
