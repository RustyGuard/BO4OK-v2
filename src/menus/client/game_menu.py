import socket
from multiprocessing import Process
from multiprocessing.connection import Connection

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.client.action_handler import ClientActionHandler
from src.client.action_sender import ClientActionSender
from src.components.base.collider import ColliderComponent
from src.components.base.decay import DecayComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.base.velocity import VelocityComponent
from src.components.chase import ChaseComponent
from src.components.fighting.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.unit_production import UnitProductionComponent
from src.components.worker.resource import ResourceComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.config import config
from src.constants import ClientCommands
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.elements.building_place import BuildMenu
from src.elements.camera_input import CameraInputHandler
from src.elements.damage_indicators import DamageIndicators
from src.elements.game_end.defeat_screen import DefeatScreen
from src.elements.game_end.victory_screen import VictoryScreen
from src.elements.minimap import Minimap
from src.elements.pause_menu import PauseMenu
from src.elements.renderers.entities_renderer import EntitiesRenderer
from src.elements.renderers.grass_background import GrassBackground
from src.elements.resources_display import ResourceDisplayMenu
from src.elements.unit_move import UnitMoveMenu
from src.elements.unit_produce import ProduceMenu
from src.main_loop_state import set_main_element
from src.sound_player import play_music
from src.systems.base.colliders import collider_system
from src.systems.base.velocity import velocity_system
from src.systems.chase import chase_system
from src.ui import UIElement
from src.ui.fps_counter import FPSCounter
from src.ui.image import UIImage


class ClientGameMenu(UIElement):
    def __init__(self, socket: socket.socket, received_actions: list[list], read_socket_process: Process,
                 write_action_connection: Connection, read_action_connection: Connection, send_process: Process,
                 players: dict[int, PlayerInfo], socket_id: int):
        super().__init__(config.screen.rect, Color(93, 161, 48))

        self.current_player = players[socket_id]

        self.sock = socket
        self.received_actions = received_actions
        self.socket_process = read_socket_process
        self.write_action_connection = write_action_connection
        self.read_action_connection = read_action_connection
        self.send_process = send_process

        fps_font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(FPSCounter(Rect(config.screen.size[0] - 100, 5, 0, 0), fps_font))

        self.action_sender = ClientActionSender(self.write_action)

        self.ecs = EntityComponentSystem()

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

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(chase_system)
        self.ecs.init_system(collider_system)

        self.camera = Camera()
        self.damage_indicators = DamageIndicators(self.camera)

        self.append_child(GrassBackground(self.camera))
        self.append_child(EntitiesRenderer(self.ecs, self.camera))

        self.append_child(self.damage_indicators)

        self.minimap = Minimap(self.ecs, self.camera, self.current_player.color)
        self.minimap_elem = UIImage(None, 'assets/ui/minimap.png')
        self.minimap_elem.bounds.bottom = config.screen.height

        self.resource_menu = ResourceDisplayMenu(self.current_player,
                                                 Rect(self.minimap.bounds.move(0, -33).topleft, (0, 0)),
                                                 Font('assets/fonts/arial.ttf', 25))

        self.build_menu = BuildMenu(self.bounds, self.resource_menu, self.action_sender,
                                    self.current_player, self.camera, self.ecs)

        self.produce_menu = ProduceMenu(self.bounds, self.ecs, self.action_sender, self.camera,
                                        self.current_player, self.resource_menu)

        self.minimap_elem.append_child(self.minimap)
        self.minimap_elem.append_child(self.resource_menu)

        self.unit_move_menu = UnitMoveMenu(
            self.ecs,
            self.action_sender,
            self.camera,
            self.current_player,
        )
        self.append_child(self.build_menu)
        self.append_child(self.produce_menu)
        self.append_child(self.unit_move_menu)
        self.append_child(self.minimap_elem)

        self.append_child(CameraInputHandler(self.camera))
        self.append_child(PauseMenu())

        self.action_handler = ClientActionHandler(self.ecs, self.current_player, self.camera)
        self.action_handler.add_hook(ClientCommands.POPUP, self.handle_show_label)
        self.action_handler.add_hook(ClientCommands.RESOURCE_INFO, lambda *_: self.resource_menu.update_values())
        self.action_handler.add_hook(ClientCommands.DEAD, self.handle_death)

        self.append_child(FPSCounter(Rect(0, 0, 150, 75), fps_font))

        self.defeat_screen = DefeatScreen()
        self.append_child(self.defeat_screen)

        self.victory_screen = VictoryScreen()
        self.append_child(self.victory_screen)

        play_music('assets/music/game1.ogg')

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

        self.ecs.update()

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.write_action_connection.close()
        self.read_action_connection.close()
        print('Closed')

    def handle_show_label(self, label: str, pos_x: int, pos_y: int, color: str):
        position = PositionComponent(pos_x, pos_y)
        self.damage_indicators.show_indicator(label, position, color)

    def handle_death(self, entity_id: EntityId):
        if self.produce_menu.selected_unit == entity_id:
            self.produce_menu.unselect()

        if entity_id in self.unit_move_menu.selected_entities:
            self.unit_move_menu.selected_entities.remove(entity_id)
