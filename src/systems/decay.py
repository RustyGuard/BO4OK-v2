from typing_extensions import TYPE_CHECKING

from src.components.decay import DecayComponent
if TYPE_CHECKING:
    from src.core.entity_component_system import EntityComponentSystem


def decay_system(entity_id: str, decay: DecayComponent, ecs: 'EntityComponentSystem'):
    if decay.frames_till_decay > 0:
        decay.frames_till_decay -= 1
    else:
        ecs.remove_entity(entity_id)
