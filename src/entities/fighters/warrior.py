import random

from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.close_range_attack import CloseRangeAttackComponent
from src.components.fighting.enemy_finder import EnemyFinderComponent
from src.components.fighting.health import HealthComponent


def create_warrior(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/warrior/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=2,
                       movement_speed=random.uniform(1, 1.5),
                       rotation_speed=7),
        EnemyFinderComponent(anger_range=750),
        HealthComponent(max_amount=75),
        CloseRangeAttackComponent(delay=30, damage=10),
        ColliderComponent(7),
    ]
