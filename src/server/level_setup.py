import math

from src.components.player_owner import PlayerOwnerComponent
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo
from src.entities import create_archer, create_warrior
from src.entities.fortress import create_fortress
from src.utils.math_utils import spread_position


def setup_level(ecs: EntityComponentSystem, players: dict[int, PlayerInfo]):
    angle_step = 2 * math.pi / len(players)
    distance_from_center = 500
    for i, player in enumerate(players.values()):
        fortress_position = (math.cos(i * angle_step) * distance_from_center,
                             math.sin(i * angle_step) * distance_from_center)

        owner = PlayerOwnerComponent(socket_id=player.socket_id,
                                     color_name=player.color_name,
                                     nick=player.nick)

        ecs.create_entity(create_fortress(fortress_position[0], fortress_position[1], owner))

        for _ in range(5):
            ecs.create_entity(create_archer(*spread_position(fortress_position, 250), owner))
            ecs.create_entity(create_warrior(*spread_position(fortress_position, 250), owner))
