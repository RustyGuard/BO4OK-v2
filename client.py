import json
import random
import socket
from multiprocessing import Process, Manager, Pipe
from string import ascii_letters
from typing import Optional

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from config import config
from constants import EVENT_UPDATE
from mod_loader import mod_loader
from ui import UIElement, FPSCounter, UIImage, Label
from core import Game, Minimap, BuildMenu, ResourceMenu


def listen(sock: socket.socket, submit_list):
    command_buffer = ''
    while True:
        try:
            command_buffer += sock.recv(1024).decode('utf8')
            print(command_buffer)
            splitter = command_buffer.find(';')
            while splitter != -1:
                command = command_buffer[:splitter]
                if command != '':
                    submit_list.append(command)
                command_buffer = command_buffer[splitter + 1:]
                splitter = command_buffer.find(';')

        except Exception as ex:
            print(ex)
            print('Disconnected')
            return


def send_function(conn, task_conn):
    while True:
        task = task_conn.recv()
        try:
            conn.send((task + ';').encode('utf8'))
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

        self.parent_conn.send(f'nick~{"".join(random.sample(list(ascii_letters), 5))}')

    def update(self, event):
        if event.type == EVENT_UPDATE:
            while self.receive_list:
                msg = self.receive_list.pop(0).split('~')
                print(msg)
                if msg[0] == 'start':
                    nicks = json.loads(msg[2])
                    self.start(int(msg[1]), nicks)
                    return
        super().update(event)

    def start(self, team_id, nicks):
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

        self.append_child(self.minimap_elem)

        self.append_child(BuildMenu(self.relative_bounds, self.game))

    def update(self, event):
        self.game.update(event)

        if event.type == EVENT_UPDATE:
            while self.receive_list:
                args = self.receive_list.pop(0).split('~')
                self.game.handle_command(args[0], args[1:])

        return super().update(event)

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
