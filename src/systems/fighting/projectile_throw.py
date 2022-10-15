from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.projectile_throw import ProjectileThrowComponent
from src.constants import SoundCode
from src.core.entity_component_system import EntityComponentSystem
from src.entities import projectiles
from src.server.action_sender import ServerActionSender
from src.utils.collision import is_close_to_target


def projectile_throw_system(projectile_throw: ProjectileThrowComponent, position: PositionComponent,
                            chase: ChaseComponent,
                            texture: TextureComponent,
                            ecs: EntityComponentSystem,
                            collider: ColliderComponent,
                            owner: PlayerOwnerComponent,
                            action_sender: ServerActionSender):
    if chase.entity_id is None:
        return

    if not is_close_to_target(ecs, chase, collider, position):
        return

    if projectile_throw.current_delay < projectile_throw.delay:
        projectile_throw.current_delay += 1
        return

    projectile_throw.current_delay = 0

    ecs.create_entity(projectiles[projectile_throw.projectile_name](position.x, position.y,
                                                                    owner, texture.rotation_angle,
                                                                    projectile_throw.arrow_speed))
    action_sender.play_sound(SoundCode.ARROW_THROW, position.to_tuple())

