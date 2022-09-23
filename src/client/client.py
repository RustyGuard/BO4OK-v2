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

from src.client.action_sender import ClientActionSender
from src.client.action_handler import ClientActionHandler
from src.components.decay import DecayComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.components.velocity import VelocityComponent
from src.config import config
from src.constants import EVENT_UPDATE
from src.core.camera import Camera
from src.core.menus.building_place import BuildMenu
from src.core.menus.unit_produce import ProduceMenu
from src.core.menus.resources_display import ResourceDisplayMenu
from src.core.minimap import Minimap
from src.core.types import PlayerInfo
from src.entity_component_system import EntityComponentSystem
from src.utils.json_utils import PydanticDecoder
from src.systems.velocity import velocity_system
from src.ui import UIElement, FPSCounter, UIImage


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
                print(msg)
                if msg[0] == 'start':
                    players = {int(i): j for i, j in msg[2].items()}
                    self.start(int(msg[1]), players)
                    return
        super().update(event)

    def start(self, team_id: int, players: dict[int, PlayerInfo]):
        w = ClientGameWindow(self.relative_bounds, self.color, self.sock, self.receive_list, self.socket_process,
                             self.parent_conn, self.child_conn, self.send_process, players, team_id)
        self.main.main_element = w

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.parent_conn.close()
        self.child_conn.close()


class ClientGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color], socket: socket.socket, received_actions: list[list],
                 read_socket_process: Process,
                 write_action_connection: Connection, read_action_connection: Connection,
                 send_process: Process, players: dict[int, PlayerInfo], socket_id: int):
        super().__init__(rect, color)
        print('dsdjfhfjkhsdjfhsfd')

        self.current_player = players[socket_id]

        self.sock = socket
        self.received_actions = received_actions
        self.socket_process = read_socket_process
        self.write_action_connection = write_action_connection
        self.read_action_connection = read_action_connection
        self.send_process = send_process

        config.reload()

        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.action_sender = ClientActionSender(self.write_action_connection)

        self.ecs = EntityComponentSystem()

        self.ecs.init_component(PositionComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DecayComponent)
        self.ecs.init_component(TextureComponent)
        self.ecs.init_component(MinimapIconComponent)
        self.ecs.init_component(UnitProductionComponent)
        self.ecs.init_component(PlayerOwnerComponent)

        self.ecs.init_system(velocity_system)

        self.action_handler = ClientActionHandler(self.ecs, self.current_player)

        self.camera = Camera()

        self.minimap = Minimap(self.ecs, self.camera)
        self.minimap_elem = UIImage(Rect(0, config['screen']['size'][1] - 388, 0, 0), 'assets/sprite/minimap.png')
        self.minimap_elem.append_child(self.minimap)

        resource_menu = ResourceDisplayMenu(self.current_player,
                                            Rect(45, 108, 0, 0),
                                            Font('assets/fonts/arial.ttf', 25))
        self.minimap_elem.append_child(resource_menu)

        menu_parent = UIElement(Rect(0, 0, 0, 0), None)
        self.append_child(menu_parent)
        menu_parent.append_child(self.minimap_elem)
        menu_parent.append_child(BuildMenu(self.relative_bounds, resource_menu, self.action_sender,
                                           self.current_player, self.camera))
        menu_parent.append_child(ProduceMenu(self.relative_bounds, self.ecs, self.action_sender, self.camera,
                                             self.current_player, resource_menu))

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
        for _, (texture, position) in self.ecs.get_entities_with_components([TextureComponent, PositionComponent]):
            texture.blit(screen, position.position_according_to_camera(self.camera))
        pygame.draw.rect(screen, pygame.Color('white'), pygame.Rect((pygame.mouse.get_pos()), (10, 10)))

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.write_action_connection.close()
        self.read_action_connection.close()
        print('Closed')
