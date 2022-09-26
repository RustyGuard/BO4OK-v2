import random

from src.components.arrow_throw import ArrowThrowComponent
from src.components.chase import ChaseComponent
from src.components.enemy_finder import EnemyFinderComponent
from src.components.health import HealthComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent


def create_archer(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/archer/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=150,
                       movement_speed=random.uniform(3, 4.5),
                       rotation_speed=20),
        HealthComponent(max_amount=50),
        ArrowThrowComponent(delay=60),
        EnemyFinderComponent(anger_range=1000),
    ]
