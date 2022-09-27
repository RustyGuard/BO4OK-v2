import json
import random
import socket
from multiprocessing import Process, Manager, Pipe
from multiprocessing.connection import Connection
from string import ascii_letters
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.client.action_handler import ClientActionHandler
from src.client.action_sender import ClientActionSender
from src.components.chase import ChaseComponent
from src.components.decay import DecayComponent
from src.components.health import HealthComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.components.velocity import VelocityComponent
from src.config import config
from src.constants import EVENT_UPDATE, EVENT_SEC, ClientCommands
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, EntityId
from src.menus.building_place import BuildMenu
from src.menus.damage_indicators import DamageIndicators
from src.menus.minimap import Minimap
from src.menus.resources_display import ResourceDisplayMenu
from src.menus.unit_move import UnitMoveMenu
from src.menus.unit_produce import ProduceMenu
from src.systems.chase import chase_system
from src.systems.velocity import velocity_system
from src.ui import UIElement, FPSCounter, UIImage
from src.utils.json_utils import PydanticDecoder


def read_server_actions(socket: socket.socket, submit_list: list[list]):
    command_buffer = ''
    while True:
        try:
            command_buffer += socket.recv(1024).decode('utf8')
            splitter = command_buffer.find(';')
            while splitter != -1:
                command = command_buffer[:splitter]
                if command != '':
                    submit_list.append(json.loads(command, cls=PydanticDecoder))
                command_buffer = command_buffer[splitter + 1:]
                splitter = command_buffer.find(';')

        except Exception as ex:
            print(ex)
            print('Disconnected')
            return


def send_function(sock: socket.socket, read_connection: Connection):
    while True:
        task = read_connection.recv()
        try:
            sock.send((json.dumps(task) + ';').encode('utf8'))
        except Exception as ex:
            print(f'Connection closed, because of {ex}')
            return


class WaitForServerWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)
        self.main = None
        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.sock = socket.socket()
        self.sock.connect(('localhost', 9090))
        print('Connected')

        manager = Manager()
        self.receive_list = manager.list()
        self.socket_process = Process(target=read_server_actions, args=(self.sock, self.receive_list))
        self.socket_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.sock, self.child_conn))
        self.send_process.daemon = True
        self.send_process.start()

        self.parent_conn.send(['nick', "".join(random.sample(list(ascii_letters), 5))])

    def update(self, event: pygame.event):
        if event.type == EVENT_UPDATE:
            while self.receive_list:
                msg = self.receive_list.pop(0)
                if msg[0] == 'start':
                    players = {int(i): j for i, j in msg[2].items()}
                    self.start(int(msg[1]), players)
                    return
        super().update(event)

    def start(self, team_id: int, players: dict[int, PlayerInfo]):
        w = ClientGameWindow(self.relative_bounds, self.sock, self.receive_list, self.socket_process, self.parent_conn,
                             self.child_conn, self.send_process, players, team_id)
        self.main.main_element = w

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.parent_conn.close()
        self.child_conn.close()


class ClientGameWindow(UIElement):
    def __init__(self, rect: Rect, socket: socket.socket, received_actions: list[list], read_socket_process: Process,
                 write_action_connection: Connection, read_action_connection: Connection, send_process: Process,
                 players: dict[int, PlayerInfo], socket_id: int):
        super().__init__(rect, Color(93, 161, 48))

        self.current_player = players[socket_id]

        self.sock = socket
        self.received_actions = received_actions
        self.socket_process = read_socket_process
        self.write_action_connection = write_action_connection
        self.read_action_connection = read_action_connection
        self.send_process = send_process

        config.reload()

        fps_font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(FPSCounter(Rect(config['screen']['size'][0] - 100, 5, 0, 0), fps_font))

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

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(chase_system)

        self.camera = Camera()
        self.damage_indicators = DamageIndicators(self.camera)

        menu_parent = UIElement(Rect(0, 0, 0, 0), None)
        self.append_child(menu_parent)

        self.minimap = Minimap(self.ecs, self.camera)
        self.minimap_elem = UIImage(Rect(0, config['screen']['size'][1] - 388, 0, 0), 'assets/sprite/minimap.png')
        self.minimap_elem.append_child(self.minimap)

        self.resource_menu = ResourceDisplayMenu(self.current_player,
                                                 Rect(45, 108, 0, 0),
                                                 Font('assets/fonts/arial.ttf', 25))
        self.minimap_elem.append_child(self.resource_menu)

        menu_parent.append_child(self.minimap_elem)

        self.build_menu = BuildMenu(self.relative_bounds, self.resource_menu, self.action_sender,
                                    self.current_player, self.camera)
        menu_parent.append_child(self.build_menu)

        self.produce_menu = ProduceMenu(self.relative_bounds, self.ecs, self.action_sender, self.camera,
                                        self.current_player, self.resource_menu)
        menu_parent.append_child(self.produce_menu)

        self.unit_move_menu = UnitMoveMenu(
            self.ecs,
            self.action_sender,
            self.camera,
            self.current_player,
        )
        menu_parent.append_child(self.unit_move_menu)

        menu_parent.append_child(self.damage_indicators)

        self.action_handler = ClientActionHandler(self.ecs, self.current_player)
        self.action_handler.add_hook(ClientCommands.DAMAGE, self.handle_damage)
        self.action_handler.add_hook(ClientCommands.RESOURCE_INFO, lambda *_: self.resource_menu.update_values())
        self.action_handler.add_hook(ClientCommands.DEAD, self.handle_death)

    def update(self, event):
        self.camera.update(event)

        if event.type == EVENT_UPDATE:
            while self.received_actions:
                args = self.received_actions.pop(0)
                self.action_handler.handle_action(args[0], args[1:])

            self.ecs.update()

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        for _, (texture, position) in self.ecs.get_entities_with_components((TextureComponent, PositionComponent)):
            texture.blit(screen, position.position_according_to_camera(self.camera))

        for _, (texture, health, position) in self.ecs.get_entities_with_components(
                (TextureComponent, HealthComponent, PositionComponent)):
            if health.amount == health.max_amount:
                continue
            health_rect = Rect(0, 0, 50, 5)
            health_rect.center = position.position_according_to_camera(self.camera)
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width = health_rect.width * health.amount / health.max_amount
            pygame.draw.rect(screen, Color('red'), health_rect)

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.write_action_connection.close()
        self.read_action_connection.close()
        print('Closed')

    def handle_damage(self, enemy_id: EntityId, victim_id: EntityId, damage: int):
        position = self.ecs.get_component(victim_id, PositionComponent)
        if position is None:
            return
        self.damage_indicators.show_indicator(damage, position)

    def handle_death(self, entity_id: EntityId):
        if self.produce_menu.selected_unit == entity_id:
            self.produce_menu.unselect()

        if entity_id in self.unit_move_menu.selected_entities:
            self.unit_move_menu.selected_entities.remove(entity_id)
