from typing import Iterable, Callable

from src.constants import ServerCommands
from src.core.types import EntityId


class ClientActionSender:
    def __init__(self, write_action_function: Callable[[list], None]):
        self.write_action_function = write_action_function

    def produce_unit(self, build_entity_id: EntityId, unit_name: str):
        self.write_action_function([ServerCommands.PRODUCE_UNIT, build_entity_id, unit_name])

    def place_building(self, build_name: str, position: tuple[float, float]):
        self.write_action_function([ServerCommands.PLACE_UNIT, build_name, *position])

    def force_to_move(self, entities: Iterable[EntityId], position: tuple[float, float]):
        self.write_action_function([ServerCommands.SET_TARGET_MOVE, list(entities), list(position)])
