from multiprocessing.connection import Connection

from src.constants import ServerCommands
from src.entity_component_system import EntityId


class ClientActionSender:
    def __init__(self, write_action_connection: Connection):
        self.write_action_connection = write_action_connection

    def produce_unit(self, build_entity_id: EntityId, unit_name: str):
        self.write_action_connection.send([ServerCommands.PRODUCE_UNIT, build_entity_id, unit_name])

    def place_building(self, build_name: str, position: tuple[float, float]):
        self.write_action_connection.send([ServerCommands.PLACE_UNIT, build_name, *position])
