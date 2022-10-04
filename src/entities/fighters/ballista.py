import random

from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.enemy_finder import EnemyFinderComponent
from src.components.fighting.health import HealthComponent
from src.components.fighting.projectile_throw import ProjectileThrowComponent


def create_ballista(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/ballista/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=350,
                       movement_speed=random.uniform(1, 1.5),
                       rotation_speed=2),
        HealthComponent(max_amount=500),
        ProjectileThrowComponent(delay=2 * 60, projectile_name='bolt'),
        EnemyFinderComponent(anger_range=1000),
    ]
