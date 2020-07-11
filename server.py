import random
import socket
from multiprocessing import Process, Manager, Pipe
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from config import config
from constants import EVENT_UPDATE
from main import Main
from ui import UIElement, FPSCounter, UIImage
from core import Game, Minimap


def connection_function(sock: socket.socket, connection_list, new_connections, receive_list):
    next_id = 0
    while True:
        conn, addr = sock.accept()
        connection_list[next_id] = (conn, addr)
        new_connections.append((next_id, conn, addr))
        send_process = Process(target=listen, args=(next_id, conn, receive_list))
        send_process.daemon = True
        send_process.start()

        print(f'Connection with id {next_id} opened')
        next_id += 1


def listen(sock_id: int, sock, submit_list):
    command_buffer = ''
    while True:
        try:
            command_buffer += sock.recv(1024).decode('utf8')
            print(command_buffer)
            splitter = command_buffer.find(';')
            while splitter != -1:
                command = command_buffer[:splitter]
                if command != '':
                    submit_list.append((sock_id, command))
                command_buffer = command_buffer[splitter + 1:]
                splitter = command_buffer.find(';')

        except Exception as ex:
            print(ex)
            print(f'Disconnected: {sock_id}')
            return


def send_function(connection_list, task_conn):
    while True:
        task = task_conn.recv()
        to_remove = []
        for i, client in connection_list.items():
            try:
                client[0].send((task + ';').encode('utf8'))
            except Exception as ex:
                to_remove.append(i)
                print(f'Connection with id {i} closed, because of {ex}')
        for i in to_remove:
            connection_list.pop(i)


class ServerGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)

        fps_font = Font('src/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.sock = socket.socket()
        self.sock.bind(('', 9090))
        self.sock.listen(1)

        manager = Manager()
        self.connection_list = manager.dict()
        self.new_connections = manager.list()
        self.receive_list = manager.list()

        self.connection_process = Process(target=connection_function, args=(self.sock, self.connection_list,
                                                                            self.new_connections, self.receive_list))
        self.connection_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.connection_list, self.child_conn))
        self.send_process.daemon = True
        self.send_process.start()

        self.game = Game(Game.Side.SERVER, send_connection=self.parent_conn, new_connections=self.new_connections)

        self.minimap = Minimap(self.game)
        self.minimap_elem = UIImage(Rect(0, 62, 0, 0), 'src/sprite/minimap.png')
        self.minimap_elem.append_child(self.minimap)

        self.append_child(self.minimap_elem)

    def update(self, event):
        self.game.update(event)

        if event.type == EVENT_UPDATE:
            while self.receive_list:
                sender, command = self.receive_list.pop(0)
                args = command.split('~')
                self.game.handle_command(args[0], args[1:], sender=sender)

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.game.draw(screen)

    def shutdown(self):
        print('Shutdown')
        self.connection_process.terminate()
        self.send_process.terminate()
        self.parent_conn.close()
        self.sock.close()


def main():
    pygame.init()
    screen = pygame.display.set_mode(config['screen']['size'])

    elem = ServerGameWindow(Rect(0, 0, *config['screen']['size']), Color('bisque'))

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
