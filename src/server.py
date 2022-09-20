import json
import random
import socket
from dataclasses import dataclass
from multiprocessing import Process, Manager, Pipe
from multiprocessing.connection import Connection
from typing import Optional, TypedDict, Any

import pygame
from pygame import Color, Vector2
from pygame.font import Font
from pygame.rect import Rect

from src.config import config
from src.constants import EVENT_UPDATE, color_name_to_pygame_color
from main import Main
from src.ui import UIElement, FPSCounter, UIImage
from src.core.minimap import Minimap
from src.core.game import Game
from src.core.types import PlayerResources, PlayerInfo
from src.entities.units_base import Fighter

from src.mod_loader import mod_loader
from src.json_utils import PydanticEncoder

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
    REQUIRED_AMOUNT_OF_PLAYERS = 2

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

    def get_players(self) -> list[PlayerInfo]:
        colors = list(color_name_to_pygame_color.keys())
        random.shuffle(colors)

        players = [
            PlayerInfo(
                color_name=colors.pop(),
                team_id=connected_player.socket_id,
                nick=connected_player.nick,
                resources=PlayerResources(
                    money=config['world']['start_money'],
                    wood=config['world']['start_wood'],
                    meat=config['world']['start_meat'],
                    max_meat=config['world']['base_meat'],
                )
            ) for connected_player in self.connected_players]

        players.append(PlayerInfo(  # Add host to game
            team_id=-1,
            color_name='black',
            nick='Admin',
            resources=PlayerResources(
                money=50000,
                wood=50000,

                meat=0,
                max_meat=50000
            )
        ))
        return players


class ServerGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color], socket: socket.socket, connections: Connections,
                 received_actions: list[tuple[int, Any]], write_action_connection: Connection, send_process: Process,
                 players: list[PlayerInfo]):
        mod_loader.import_mods()

        super().__init__(rect, color)

        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.socket = socket
        self.connections = connections
        self.received_actions = received_actions
        self.write_action_connection = write_action_connection
        self.send_process = send_process

        self.game = Game(Game.Side.SERVER, mod_loader, self.write_action_connection, players, -1)

        self.minimap_elem = UIImage(Rect(0, config['screen']['size'][1] - 388, 0, 0), 'assets/sprite/minimap.png')

        self.minimap = Minimap(self.game)
        self.minimap_elem.append_child(self.minimap)

        self.append_child(self.minimap_elem)
        self.game.create_unit('warrior', (0, 0))
        self.game.create_unit('fortress', (500, 0))
        self.game.create_unit('fortress', (-500, 0))
        self.game.create_unit('archer', (-25, -25))
        self.game.create_unit('archer', (25, -25))
        self.game.create_unit('archer', (-25, 25))
        self.game.create_unit('archer', (25, 25))

    def update(self, event: pygame.event) -> bool:
        self.game.update(event)

        if event.type == EVENT_UPDATE:
            while self.received_actions:
                sender, command = self.received_actions.pop(0)
                self.handle_command(command[0], command[1:], socket_id=sender)

        return super().update(event)

    def handle_command(self, command: str, args: list[Any], socket_id: int) -> None:
        print(command, args, socket_id)
        if command == Game.ServerCommands.PLACE_UNIT:
            self.game.place_unit(args[0], (args[1], args[2]), socket_id)

        elif command == Game.ServerCommands.SET_TARGET_MOVE:
            unit = self.game.find_with_id(args[0])
            self.game.set_target(unit, (Fighter.Target.MOVE, Vector2(args[1], args[2])))

        elif command == Game.ServerCommands.PRODUCE_UNIT:
            prod_build = self.game.find_with_id(args[0])
            unit_name = args[1]

            try:
                prod_build.add_to_queue(unit_name)
            except AttributeError:
                print(f'add_to_queue not provided to {prod_build.__class__.__name__}')

        else:
            print('Unexpected command', command, args)

    def draw(self, screen) -> None:
        super().draw(screen)
        self.game.draw(screen)

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
