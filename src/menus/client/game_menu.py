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
from src.constants import ClientCommands, EVENT_UPDATE
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.elements.building_place import BuildMenu
from src.elements.camera_input import CameraInputHandler
from src.elements.damage_indicators import DamageIndicators
from src.elements.entities_renderer import EntitiesRenderer
from src.elements.grass_background import GrassBackground
from src.elements.minimap import Minimap
from src.elements.pause_menu import PauseMenu
from src.elements.resources_display import ResourceDisplayMenu
from src.elements.unit_move import UnitMoveMenu
from src.elements.unit_produce import ProduceMenu
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
        super().__init__(config.screen.get_rect(), Color(93, 161, 48))

        self.current_player = players[socket_id]

        self.sock = socket
        self.received_actions = received_actions
        self.socket_process = read_socket_process
        self.write_action_connection = write_action_connection
        self.read_action_connection = read_action_connection
        self.send_process = send_process

        fps_font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(FPSCounter(Rect(config.screen.size[0] - 100, 5, 0, 0), fps_font))

        self.action_sender = ClientActionSender(self.write_action_connection)

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

        menu_parent = UIElement()
        self.append_child(menu_parent)

        menu_parent.append_child(self.damage_indicators)

        self.minimap = Minimap(self.ecs, self.camera, self.current_player.color)
        self.minimap_elem = UIImage(Rect(0, config.screen.size[1] - 388, 0, 0), 'assets/sprite/minimap.png')

        self.resource_menu = ResourceDisplayMenu(self.current_player,
                                                 Rect(45, 108, 0, 0),
                                                 Font('assets/fonts/arial.ttf', 25))

        self.build_menu = BuildMenu(self.relative_bounds, self.resource_menu, self.action_sender,
                                    self.current_player, self.camera)

        self.produce_menu = ProduceMenu(self.relative_bounds, self.ecs, self.action_sender, self.camera,
                                        self.current_player, self.resource_menu)

        self.minimap_elem.append_child(self.minimap)
        self.minimap_elem.append_child(self.resource_menu)

        self.unit_move_menu = UnitMoveMenu(
            self.ecs,
            self.action_sender,
            self.camera,
            self.current_player,
        )
        menu_parent.append_child(self.build_menu)
        menu_parent.append_child(self.produce_menu)
        menu_parent.append_child(self.unit_move_menu)
        menu_parent.append_child(self.minimap_elem)
        self.append_child(CameraInputHandler(self.camera))
        self.append_child(PauseMenu())

        self.action_handler = ClientActionHandler(self.ecs, self.current_player)
        self.action_handler.add_hook(ClientCommands.POPUP, self.handle_show_label)
        self.action_handler.add_hook(ClientCommands.RESOURCE_INFO, lambda *_: self.resource_menu.update_values())
        self.action_handler.add_hook(ClientCommands.DEAD, self.handle_death)

    def update(self, event):
        if event.type == EVENT_UPDATE:
            while self.received_actions:
                args = self.received_actions.pop(0)
                self.action_handler.handle_action(args[0], args[1:])

            self.ecs.update()

        return super().update(event)

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
