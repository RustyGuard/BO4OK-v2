from dataclasses import dataclass

from src.components.base.position import PositionComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId


@dataclass(slots=True)
class ChaseComponent:
    distance_until_attack: float
    movement_speed: float
    rotation_speed: int  # in degrees
    chase_position: PositionComponent | None = None
    entity_id: EntityId | None = None

    def assemble_on_client(self, ecs: EntityComponentSystem):
        if self.chase_position is None:
            return
        if self.entity_id:
            self.chase_position = ecs.get_component(self.entity_id, PositionComponent)
            return
        self.chase_position = PositionComponent(**self.chase_position)

    def drop_target(self):
        self.chase_position = None
        self.entity_id = None
