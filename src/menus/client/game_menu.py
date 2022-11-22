import socket
from multiprocessing import Process
from multiprocessing.connection import Connection

from src.client.action_handler import ClientActionHandler
from src.client.action_sender import ClientActionSender
from src.components.base.collider import ColliderComponent
from src.components.base.decay import DecayComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.base.velocity import VelocityComponent
from src.components.chase import ChaseComponent
from src.components.core_building import CoreBuildingComponent
from src.components.fighting.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.unit_production import UnitProductionComponent
from src.components.worker.resource import ResourceComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.constants import ClientCommands
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId, Component
from src.elements.game_composer import GameComposer
from src.main_loop_state import set_main_element
from src.sound_player import play_music
from src.systems.base.colliders import collider_system
from src.systems.base.velocity import velocity_system
from src.systems.chase import chase_system
from src.ui import UIElement


class ClientGameMenu(UIElement):
    def _init_ecs(self):
        self.ecs.init_component(PositionComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DecayComponent)
        self.ecs.init_component(TextureComponent)
        self.ecs.init_component(MinimapIconComponent)
        self.ecs.init_component(UnitProductionComponent)
        self.ecs.init_component(PlayerOwnerComponent)
        self.ecs.init_component(ChaseComponent)
        self.ecs.init_component(HealthComponent)
        self.ecs.init_component(ResourceComponent)
        self.ecs.init_component(UncompletedBuildingComponent)
        self.ecs.init_component(ColliderComponent)
        self.ecs.init_component(CoreBuildingComponent)

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(chase_system)
        self.ecs.init_system(collider_system)

    def __init__(self, connection_to_server: socket.socket, received_actions: list[list], read_socket_process: Process,
                 write_action_connection: Connection, read_action_connection: Connection, send_process: Process,
                 players: dict[int, PlayerInfo], socket_id: int):
        super().__init__()

        self.current_player = players[socket_id]

        self.sock = connection_to_server
        self.received_actions = received_actions
        self.socket_process = read_socket_process
        self.write_action_connection = write_action_connection
        self.read_action_connection = read_action_connection
        self.send_process = send_process

        self.action_sender = ClientActionSender(self.write_action)

        self.ecs = EntityComponentSystem(on_create=self.on_create)
        self._init_ecs()

        self.game_composer = GameComposer(self.ecs, self.current_player, self.action_sender)
        self.append_child(self.game_composer)

        self.action_handler = ClientActionHandler(self.ecs, self.current_player, self.game_composer.camera)
        self.action_handler.add_hook(ClientCommands.POPUP, self.handle_show_label)
        self.action_handler.add_hook(ClientCommands.RESOURCE_INFO, lambda *_: self.game_composer.resource_menu.update_values())
        self.action_handler.add_hook(ClientCommands.DEAD, self.handle_death)
        self.action_handler.add_hook(ClientCommands.DEFEAT, self.game_composer.show_defeat_screen)
        self.action_handler.add_hook(ClientCommands.VICTORY, self.game_composer.show_victory_screen)

        play_music('assets/music/game1.ogg')

    def on_create(self, entity_id, components: list[Component]):
        self.game_composer.camera.check_if_fortress_appeared(self.ecs, self.current_player)

    def write_action(self, action: list):
        self.write_action_connection.send(action)

    def on_update(self):
        while self.received_actions:
            command, *args = self.received_actions.pop(0)

            if command == 'disconnect':
                from src.menus.main_menu import MainMenu
                set_main_element(MainMenu())
                return

            self.action_handler.handle_action(command, args)

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.write_action_connection.close()
        self.read_action_connection.close()
        print('Closed')

    def handle_show_label(self, label: str, pos_x: int, pos_y: int, color: str):
        position = PositionComponent(pos_x, pos_y)
        self.game_composer.damage_indicators.show_indicator(label, position, color)

    def handle_death(self, entity_id: EntityId):
        self.game_composer.produce_menu.on_death(entity_id)
        self.game_composer.unit_move_menu.on_death(entity_id)
