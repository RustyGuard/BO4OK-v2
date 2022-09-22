import math

from src.core.types import PlayerInfo
from src.entities.fortress import create_fortress
from src.entity_component_system import EntityComponentSystem


def setup_level(ecs: EntityComponentSystem, players: dict[int, PlayerInfo]):
    angle_step = 2 * math.pi / len(players)
    distance_from_center = 500
    for i, player in enumerate(players.values()):
        ecs.create_entity(create_fortress(math.cos(i * angle_step) * distance_from_center,
                                          math.sin(i * angle_step) * distance_from_center,
                                          player_socket_id=player.socket_id,
                                          player_color_name=player.color_name,
                                          player_nick=player.nick))
