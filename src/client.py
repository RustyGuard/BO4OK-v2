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

from src.config import config
from src.constants import EVENT_UPDATE
from src.json_utils import PydanticDecoder
from src.mod_loader import mod_loader
from src.ui import UIElement, FPSCounter, UIImage
from src.core.menus import BuildMenu, ProduceMenu, ResourceMenu
from src.core.minimap import Minimap
from src.core.game import Game


def listen(sock: socket.socket, submit_list: list[list]):
    command_buffer = ''
    while True:
        try:
            command_buffer += sock.recv(1024).decode('utf8')
            print(command_buffer)
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


def send_function(sock: socket.socket, task_conn: Connection):
    while True:
        task, _ = task_conn.recv()
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
        self.socket_process = Process(target=listen, args=(self.sock, self.receive_list))
        self.socket_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.sock, self.child_conn))
        self.send_process.daemon = True
        self.send_process.start()

        self.parent_conn.send((['nick', "".join(random.sample(list(ascii_letters), 5))], None))

    def update(self, event: pygame.event):
        if event.type == EVENT_UPDATE:
            while self.receive_list:
                msg = self.receive_list.pop(0)
                print(msg)
                if msg[0] == 'start':
                    nicks = msg[2]
                    print(f'{nicks=}')
                    self.start(int(msg[1]), nicks)
                    return
        super().update(event)

    def start(self, team_id: int, nicks):
        print(team_id, nicks)
        w = ClientGameWindow(self.relative_bounds, self.color, self.sock, self.receive_list, self.socket_process,
                             self.parent_conn, self.child_conn, self.send_process, nicks, team_id)
        self.main.main_element = w

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.parent_conn.close()
        self.child_conn.close()


class ClientGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color], sock, receive_list, socket_process, parent_conn, child_conn,
                 send_process, nicks, team_id):
        super().__init__(rect, color)

        self.sock = sock
        self.receive_list = receive_list
        self.socket_process = socket_process
        self.parent_conn = parent_conn
        self.child_conn = child_conn
        self.send_process = send_process

        mod_loader.import_mods()

        config.reload()

        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.game = Game(Game.Side.CLIENT, mod_loader, self.parent_conn, nicks, team_id)

        self.minimap = Minimap(self.game)
        self.minimap_elem = UIImage(Rect(0, config['screen']['size'][1] - 388, 0, 0), 'assets/sprite/minimap.png')
        self.minimap_elem.append_child(self.minimap)

        self.minimap_elem.append_child(ResourceMenu(self.game.current_player,
                                                    Rect(45, 108, 0, 0),
                                                    Font('assets/fonts/arial.ttf', 25)))

        menu_parent = UIElement(Rect(0, 0, 0, 0), None)
        self.append_child(menu_parent)
        menu_parent.append_child(self.minimap_elem)
        menu_parent.append_child(BuildMenu(self.relative_bounds, self.game))
        menu_parent.append_child(ProduceMenu(self.relative_bounds, self.game))

    def update(self, event):
        self.game.update(event)

        if event.type == EVENT_UPDATE:
            while self.receive_list:
                args = self.receive_list.pop(0)
                self.handle_command(args[0], args[1:])

        return super().update(event)

    def handle_command(self, command, args):
        if command == Game.ClientCommands.CREATE:
            self.game.load_unit(args)

        elif command == Game.ClientCommands.UPDATE:
            unit = self.game.find_with_id(args[1])
            if unit is not None:
                unit.set_update_args(args[3])
            else:
                print('\t[ALERT] It is ghoust! I am scared!', args)
                self.game.load_unit(args)

        elif command == Game.ClientCommands.TARGET_CHANGE:
            unit = self.game.find_with_id(args[0])
            unit.target = unit.decode_target(args[1])
        elif command == Game.ClientCommands.TARGET_CHANGE:
            unit = self.game.find_with_id(args[0])
            unit.target = unit.decode_target(args[1])

        elif command == Game.ClientCommands.RESOURCE_INFO:
            player = self.game.current_player
            for attr in ['meat', 'money', 'wood', 'max_meat']:
                if val := args[0].get(attr, None):
                    setattr(player.resources, attr, val)

        elif command == Game.ClientCommands.HEALTH_INFO:
            unit = self.game.find_with_id(args[0])
            unit.health = float(args[1])
            unit.max_health = float(args[2])

        elif command == Game.ClientCommands.DEAD:
            unit = self.game.find_with_id(args[0])
            self.game.sprites.remove(unit)
            print(unit, args[0], 'dead')

        else:
            print('Unexpected command', command, 'args:', args)

    def draw(self, screen):
        super().draw(screen)
        self.game.draw(screen)

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.parent_conn.close()
        self.child_conn.close()
        print('Closed')
