from src.components.arrow_throw import ArrowThrowComponent
from src.components.chase import ChaseComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.core.entity_component_system import EntityComponentSystem
from src.entities import create_arrow


def arrow_throw_system(arrow_throw: ArrowThrowComponent, position: PositionComponent, chase: ChaseComponent,
                       texture: TextureComponent,
                       ecs: EntityComponentSystem,
                       owner: PlayerOwnerComponent):
    if chase.entity_id is None:
        return

    if chase.chase_position.distance(position) > chase.distance_until_attack:
        return

    arrow_throw.current_delay += 1
    if arrow_throw.current_delay >= arrow_throw.delay:
        arrow_throw.current_delay = 0

        ecs.create_entity(create_arrow(position.x, position.y, owner, texture.rotation_angle, arrow_throw.arrow_speed))
