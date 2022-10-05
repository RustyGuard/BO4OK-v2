import random

from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.enemy_finder import EnemyFinderComponent
from src.components.fighting.health import HealthComponent
from src.components.fighting.projectile_throw import ProjectileThrowComponent


def create_archer(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/archer/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=250,
                       movement_speed=random.uniform(6, 7),
                       rotation_speed=20),
        HealthComponent(max_amount=50),
        ProjectileThrowComponent(delay=60, projectile_name='arrow'),
        EnemyFinderComponent(anger_range=1000),
        ColliderComponent(7),
    ]
