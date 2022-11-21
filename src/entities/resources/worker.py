import random

from src.components.base.collider import ColliderComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.health import HealthComponent
from src.components.worker.resource_gatherer import ResourceGathererComponent
from src.components.worker.work_finder import WorkFinderComponent


def create_worker(x: float, y: float, player_owner: PlayerOwnerComponent):
    return [
        PositionComponent(x, y),
        player_owner,
        TextureComponent.create_from_filepath(f'assets/unit/worker/{player_owner.color_name}.png'),
        ChaseComponent(distance_until_attack=0,
                       movement_speed=random.uniform(1, 1.5),
                       rotation_speed=7),
        WorkFinderComponent(),
        HealthComponent(max_amount=75),
        ResourceGathererComponent(60, 5, 50, 50),
        ColliderComponent(7),
    ]
