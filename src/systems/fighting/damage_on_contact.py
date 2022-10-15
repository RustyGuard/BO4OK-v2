from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.fighting.damage_on_contact import DamageOnContactComponent
from src.components.fighting.health import HealthComponent
from src.constants import SoundCode
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
        action_sender.show_popup(str(damage_on_contact.damage), enemy_position, 'red')

        if damage_on_contact.die_on_contact:
            ecs.remove_entity(entity_id)
            action_sender.play_sound(SoundCode.ARROW_CONTACT, position.to_tuple())

            return
