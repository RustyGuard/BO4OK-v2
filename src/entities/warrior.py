import random

from src.components.chase import ChaseComponent
from src.components.close_range_attack import CloseRangeAttack
from src.components.enemy_finder import EnemyFinderComponent
from src.components.health import HealthComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_warrior(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/warrior/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=50,
                       movement_speed=random.uniform(1, 1.5),
                       rotation_speed=7),
        EnemyFinderComponent(anger_range=750),
        HealthComponent(max_amount=75),
        CloseRangeAttack(delay=30, damage=10),
    ]
