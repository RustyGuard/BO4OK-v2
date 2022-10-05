import math

from src.components.base.collider import ColliderComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.core.entity_component_system import EntityComponentSystem
from src.utils.math_utils import convert_to_main_angle

ticks_to_update = 3
ticks = 0

angle_neighborhood = 60


def collider_system(collider: ColliderComponent, position: PositionComponent,
                    ecs: EntityComponentSystem):
    if not collider.static:
        return

    for _, (entity_position, entity_collider, entity_texture) in ecs.get_entities_with_components((PositionComponent,
                                                                                                   ColliderComponent,
                                                                                                   TextureComponent)):
        if entity_collider.static:
            continue

        distance = position.distance(entity_position)
        if distance >= (collider.radius + entity_collider.radius):
            continue

        angle = position.angle_between(entity_position)
        angle_diff = convert_to_main_angle(angle - entity_texture.rotation_angle)

        if 180 - angle_neighborhood <= angle_diff <= 180:
            angle -= 1
        elif 180 < angle_diff <= 180 + angle_neighborhood:
            angle += 1

        entity_position.x = position.x + math.cos(math.radians(angle)) * (collider.radius + entity_collider.radius)
        entity_position.y = position.y - math.sin(math.radians(angle)) * (collider.radius + entity_collider.radius)
