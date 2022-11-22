from pygame import Rect

from src.components.base.collider import ColliderComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.core.entity_component_system import EntityComponentSystem


def is_close_to_target(ecs: EntityComponentSystem,
                       chase: ChaseComponent, collider: ColliderComponent, position: PositionComponent):
    if chase.entity_id not in ecs._entities:
        return False

    enemy_collider = ecs.get_component(chase.entity_id, ColliderComponent)
    if enemy_collider:
        distance = enemy_collider.radius + collider.radius
    else:
        enemy_texture = ecs.get_component(chase.entity_id, TextureComponent)
        distance = enemy_texture.texture.get_width() // 2 + collider.radius

    distance += chase.distance_until_attack
    return position.distance(chase.chase_position) <= distance


def can_be_placed(ecs: EntityComponentSystem, position: tuple[float, float], size: tuple[float, float]):
    place_position = Rect((0, 0), size)
    place_position.center = position
    for _, (texture, entity_position) in ecs.get_entities_with_components((TextureComponent, PositionComponent)):
        rect = texture.texture.get_rect()
        rect.center = entity_position.to_tuple()

        if rect.colliderect(place_position):
            return False
    return True
