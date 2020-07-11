import socket
from multiprocessing import Process, Manager, Pipe
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from config import config
from constants import EVENT_UPDATE
from ui import UIElement, FPSCounter, UIImage
from core import Game, Minimap


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


class ClientGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)
        config.reload()

        fps_font = Font('src/fonts/arial.ttf', 20)

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

        self.game = Game(Game.Side.CLIENT, self.parent_conn)

        self.minimap = Minimap(self.game)
        self.minimap_elem = UIImage(Rect(0, 62, 0, 0), 'src/sprite/minimap.png')
        self.minimap_elem.append_child(self.minimap)

        self.append_child(self.minimap_elem)

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
        self.socket_process.terminate()
        self.sock.close()
