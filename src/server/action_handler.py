from typing import Any

from src.constants import ServerCommands
from src.entity_component_system import EntityComponentSystem


class ServerActionHandler:
    def __init__(self, ecs: EntityComponentSystem):
        self.ecs = ecs

    def handle_action(self, command: str, args: list[Any], socket_id: int):
        pass
