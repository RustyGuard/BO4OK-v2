import math

from src.components.base.player_owner import PlayerOwnerComponent
from src.config import config
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo
from src.entities import create_archer, create_warrior
from src.entities.buildings.fortress import create_fortress
from src.entities.resources.mine import create_mine
from src.entities.resources.tree import create_tree
from src.utils.collision import can_be_placed
from src.utils.math_utils import spread_position


def setup_level(ecs: EntityComponentSystem, players: dict[int, PlayerInfo]):
    angle_step = 2 * math.pi / len(players)
    distance_from_center = 1000
    for i, player in enumerate(players.values()):
        fortress_position = (math.cos(i * angle_step) * distance_from_center,
                             math.sin(i * angle_step) * distance_from_center)

        owner = PlayerOwnerComponent(socket_id=player.socket_id,
                                     color_name=player.color_name,
                                     nick=player.nick)

        ecs.create_entity(create_fortress(*fortress_position, owner))
        ecs.create_entity(create_mine(math.cos(i * angle_step) * distance_from_center * 0.75,
                             math.sin(i * angle_step) * distance_from_center * 0.75))

        # if player.nick != 'Admin':
        #     continue
        for _ in range(5):
            ecs.create_entity(create_archer(*spread_position(fortress_position, 250), owner))
            ecs.create_entity(create_warrior(*spread_position(fortress_position, 250), owner))

    for i in range(300):
        while True:
            tree_position = spread_position((0, 0), config.world.size)
            if can_be_placed(ecs, tree_position, (16, 16)):
                ecs.create_entity(create_tree(*tree_position))
                break
