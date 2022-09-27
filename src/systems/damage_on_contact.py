from src.components.damage_on_contact import DamageOnContactComponent
from src.components.health import HealthComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId
from src.server.action_sender import ServerActionSender

DELAY_BETWEEN_CHECKS = 10


def damage_on_contact_system(entity_id: EntityId,
                             damage_on_contact: DamageOnContactComponent,
                             owner: PlayerOwnerComponent,
                             position: PositionComponent,
                             ecs: EntityComponentSystem,
                             texture: TextureComponent,
                             action_sender: ServerActionSender
                             ):
    damage_on_contact.check_delay += 1
    if damage_on_contact.check_delay < DELAY_BETWEEN_CHECKS:
        return

    damage_on_contact.check_delay = 0
    for enemy_id, (enemy_health, enemy_owner, enemy_position, enemy_texture) in ecs.get_entities_with_components(
            (HealthComponent, PlayerOwnerComponent, PositionComponent, TextureComponent)):

        if enemy_owner == owner:
            continue

        rect = texture.texture.get_rect()
        rect.center = position.to_tuple()
        enemy_rect = enemy_texture.texture.get_rect()
        enemy_rect.center = enemy_position.to_tuple()
        if not enemy_rect.colliderect(rect):
            continue

        enemy_health.apply_damage(damage_on_contact.damage)
        action_sender.update_component_info(enemy_id, enemy_health)
        action_sender.apply_damage(entity_id, enemy_id, damage_on_contact.damage)

        if damage_on_contact.die_on_contact:
            ecs.remove_entity(entity_id)

            return
