import json
import random
import socket
from dataclasses import dataclass
from multiprocessing import Process, Manager, Pipe
from multiprocessing.connection import Connection
from typing import Optional, Any

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.components.decay import DecayComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.components.velocity import VelocityComponent
from src.config import config
from src.constants import EVENT_UPDATE, color_name_to_pygame_color, EVENT_SEC

from src.entities.arrow import create_arrow
from src.entity_component_system import EntityComponentSystem, Component, EntityId
from src.main import Main
from src.server.action_handler import ServerActionHandler
from src.server.action_sender import ServerActionSender
from src.server.level_setup import setup_level
from src.systems.decay import decay_system
from src.systems.unit_production import unit_production_system
from src.systems.velocity import velocity_system
from src.ui import UIElement, FPSCounter
from src.core.types import PlayerResources, PlayerInfo

from src.utils.json_utils import PydanticEncoder

Connections = dict[int, tuple[socket.socket, Any]]


def wait_for_new_connections(socket: socket.socket, connections: Connections,
                             received_actions: list[tuple[int, Any]]):
    next_id = 0
    while True:
        conn, addr = socket.accept()
        connections[next_id] = (conn, addr)
        send_process = Process(target=receive_data_from_socket, args=(next_id, conn, received_actions), daemon=True)
        send_process.start()

        print(f'Connection with id {next_id} opened')
        next_id += 1


def receive_data_from_socket(socket_id: int, socket: socket.socket, submit_list: list[tuple[int, Any]]):
    command_buffer = ''
    while True:
        try:
            command_buffer += socket.recv(1024).decode('utf8')
            print(command_buffer)
            splitter = command_buffer.find(';')
            while splitter != -1:
                command = command_buffer[:splitter]
                if command != '':
                    submit_list.append((socket_id, json.loads(command)))
                command_buffer = command_buffer[splitter + 1:]
                splitter = command_buffer.find(';')

        except Exception as ex:
            print(ex)
            print(f'Disconnected: {socket_id}')
            return


def send_player_actions(connections: Connections, read_connection: Connection):
    while True:
        task, socket_id = read_connection.recv()
        if socket_id is not None:
            try:
                connections[socket_id][0].send((json.dumps(task, cls=PydanticEncoder) + ';').encode('utf8'))
            except IndexError:
                print(f'No player with id: {socket_id}')
        else:
            to_remove = []
            for i, client in connections.items():
                try:
                    client[0].send((json.dumps(task) + ';').encode('utf8'))
                except Exception as ex:
                    to_remove.append(i)
                    print(f'Connection with id {i} closed, because of {ex}')
            for i in to_remove:
                connections.pop(i)


@dataclass
class ConnectedPlayer:
    socket_id: int
    nick: str


class WaitForPlayersWindow(UIElement):
    REQUIRED_AMOUNT_OF_PLAYERS = 1

    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)
        self.main = None
        self.connected_players: list[ConnectedPlayer] = []
        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.sock = socket.socket()
        self.sock.bind((config['server']['ip'], config['server']['port']))
        self.sock.listen(1)

        manager = Manager()
        self.connections: Connections = manager.dict()
        self.received_actions: list[tuple[int, Any]] = manager.list()

        self.connection_process = Process(target=wait_for_new_connections, args=(self.sock, self.connections,
                                                                                 self.received_actions))
        self.connection_process.start()

        self.write_action_connection, self.read_connection = Pipe()
        self.send_process = Process(target=send_player_actions, args=(self.connections, self.read_connection),
                                    daemon=True)
        self.send_process.start()

    def is_all_nicks_sent(self):
        connected_player_ids = {player.socket_id for player in self.connected_players}
        connected_sockets = set(self.connections.keys())

        return connected_player_ids == connected_sockets

    def update(self, event):
        super().update(event)
        if event.type == EVENT_UPDATE:
            while self.received_actions:
                sock_id, msg = self.received_actions.pop(0)
                print(msg)
                if msg[0] == 'nick':
                    self.connected_players.append(ConnectedPlayer(
                        socket_id=sock_id,
                        nick=msg[1]
                    ))
                if len(self.connections) >= self.REQUIRED_AMOUNT_OF_PLAYERS and self.is_all_nicks_sent():
                    self.start()
                    return

    def start(self):
        self.connection_process.terminate()

        players = self.get_players()

        for socket_id in self.connections:
            self.write_action_connection.send((['start', socket_id, players], socket_id))

        w = ServerGameWindow(self.relative_bounds, self.color, self.sock, self.connections, self.received_actions,
                             self.write_action_connection, self.send_process, players)
        self.main.main_element = w

    def get_players(self) -> dict[int, PlayerInfo]:
        colors = list(color_name_to_pygame_color.keys())
        random.shuffle(colors)

        players = {
            connected_player.socket_id:
                PlayerInfo(
                    color_name=colors.pop(),
                    socket_id=connected_player.socket_id,
                    nick=connected_player.nick,
                    resources=PlayerResources(
                        money=config['world']['start_money'],
                        wood=config['world']['start_wood'],
                        meat=config['world']['start_meat'],
                        max_meat=config['world']['base_meat'],
                    )
                ) for connected_player in self.connected_players}

        players[-1] = PlayerInfo(  # Add host to game
            socket_id=-1,
            color_name='black',
            nick='Admin',
            resources=PlayerResources(
                money=50000,
                wood=50000,

                meat=0,
                max_meat=50000
            )
        )
        return players


class ServerGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color], socket: socket.socket, connections: Connections,
                 received_actions: list[tuple[int, Any]], write_action_connection: Connection, send_process: Process,
                 players: dict[int, PlayerInfo]):
        super().__init__(rect, color)

        self.players = players

        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.socket = socket
        self.connections = connections
        self.received_actions = received_actions
        self.write_action_connection = write_action_connection
        self.send_process = send_process

        self.action_sender = ServerActionSender(self.write_action_connection)

        self.ecs = EntityComponentSystem(self.on_create, self.on_remove)

        self.ecs.init_component(PositionComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DecayComponent)
        self.ecs.init_component(TextureComponent)
        self.ecs.init_component(MinimapIconComponent)
        self.ecs.init_component(UnitProductionComponent)
        self.ecs.init_component(PlayerOwnerComponent)

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(decay_system)
        self.ecs.init_system(unit_production_system)

        self.action_handler = ServerActionHandler(self.ecs, self.players, self.action_sender)

        # self.minimap_elem = UIImage(Rect(0, config['screen']['size'][1] - 388, 0, 0), 'assets/sprite/minimap.png')
        #
        # self.minimap = Minimap(self.game)
        # self.minimap_elem.append_child(self.minimap)
        #
        # self.append_child(self.minimap_elem)
        setup_level(self.ecs, self.players)

    def on_create(self, entity_id, components: list[Component]):
        components_to_exclude = (
            DecayComponent,

        )
        components = [component for component in components if type(component) not in components_to_exclude]

        self.action_sender.send_entity(entity_id, components)

    def on_remove(self, entity_id: EntityId):
        self.action_sender.remove_entity(entity_id)

    def update(self, event: pygame.event) -> bool:
        if event.type == EVENT_UPDATE:
            while self.received_actions:
                sender, command = self.received_actions.pop(0)
                self.action_handler.handle_action(command[0], command[1:], sender)

            self.ecs.update()

        return super().update(event)

    def draw(self, screen) -> None:
        super().draw(screen)
        for _, (texture, position) in self.ecs.get_entities_with_components([TextureComponent, PositionComponent]):
            texture.blit(screen, position.to_tuple())

    def shutdown(self) -> None:
        print('Shutdown')
        self.send_process.terminate()
        self.write_action_connection.close()
        self.socket.close()


def main():
    pygame.init()
    screen = pygame.display.set_mode(config['screen']['size'])

    elem = WaitForPlayersWindow(Rect(0, 0, *config['screen']['size']), Color('bisque'))

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
