from typing import Any

from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.components.fighting.health import HealthComponent
from src.components.unit_production import UnitProductionComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.constants import ServerCommands
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId, PlayerState
from src.entities import buildings, entity_icons
from src.server.action_sender import ServerActionSender
from src.utils.collision import can_be_placed
from src.utils.image import get_image
from src.utils.math_utils import spread_position


class ServerActionHandler:
    def __init__(self, ecs: EntityComponentSystem, players: dict[int, PlayerInfo], action_sender: ServerActionSender):
        self.ecs = ecs
        self.players = players
        self.action_sender = action_sender

    def handle_action(self, command: str, args: list[Any], socket_id: int):
        player = self.players[socket_id]

        if command == ServerCommands.PRODUCE_UNIT:
            self.handle_produce(player, args[0], args[1])
        elif command == ServerCommands.PLACE_UNIT:
            self.handle_place(player, args[0], args[1], args[2])
        elif command == ServerCommands.SET_TARGET_MOVE:
            self.handle_force_move(player, args[0], tuple(args[1]))

        else:
            print(f'Unknown command: {command}({args})')

    def handle_produce(self, player: PlayerInfo, build_entity_id: EntityId, unit_name: str):
        if player.current_state == PlayerState.SPECTATOR:
            print(f'''{player=} trying to produce units in spectator''')
            return

        components = self.ecs.get_components(build_entity_id, (UnitProductionComponent, PlayerOwnerComponent))
        if components is None:
            print(f'This entity({build_entity_id=}) can not produce anything, you are stupid, {player=}')
            return

        producing_component, owner_component = components
        if owner_component.socket_id != player.socket_id:
            print(f'''{player=} trying to produce units in other's({owner_component.socket_id}) building''')
            return

        if producing_component.add_to_queue(unit_name, player):
            self.action_sender.update_resource_info(player)
            self.action_sender.update_component_info(build_entity_id, producing_component)

    def handle_place(self, player: PlayerInfo, build_name: str, position_x: float, position_y: float):
        if player.current_state == PlayerState.SPECTATOR:
            print(f'''{player=} trying to build in spectator''')
            return

        cost = buildings[build_name]
        if not player.has_enough(cost):
            return

        building_texture_path = entity_icons[build_name].format(color_name=player.color_name)
        building_texture = get_image(building_texture_path)

        if not can_be_placed(self.ecs, (position_x, position_y), building_texture.get_rect().size):
            print('Can not build on top of entity')
            return

        self.ecs.create_entity([
            PositionComponent(position_x, position_y),
            UncompletedBuildingComponent(build_name, 10),
            TextureComponent.create_from_filepath(building_texture_path),
            PlayerOwnerComponent(
                socket_id=player.socket_id,
                color_name=player.color_name,
                nick=player.nick,
            ),
            HealthComponent(150),
        ])

        player.spend(cost)
        self.action_sender.update_resource_info(player)

    def handle_force_move(self, player: PlayerInfo, entities: list[EntityId], position: tuple[float, float]):
        if player.current_state == PlayerState.SPECTATOR:
            print(f'''{player=} trying to build in spectator''')
            return

        for entity_id in entities:
            components = self.ecs.get_components(entity_id, (ChaseComponent, PlayerOwnerComponent))
            if components is None:
                print(f'This entity({entity_id=}) can not chase anything, you are stupid, {player=}')
                return
            chase, owner_component = components

            if owner_component.socket_id != player.socket_id:
                print(
                    f'''{player=} trying to force to move {entity_id=} in other's({owner_component.socket_id}) team''')
                return

            chase.chase_position = PositionComponent(*spread_position(position, 50))
            chase.entity_id = None

            self.action_sender.update_component_info(entity_id, chase)
