import random
import socket
from multiprocessing import Process, Manager, Pipe
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from config import config
from main import Main
from ui import UIElement, FPSCounter
from core import Game, Camera, Minimap


def connection_function(sock: socket.socket, connection_list):
    next_id = 0
    while True:
        conn, addr = sock.accept()
        connection_list[next_id] = (conn, addr)
        print(f'Connection with id {next_id} opened')
        next_id += 1


def send_function(connection_list, task_conn):
    while True:
        task = task_conn.recv()
        to_remove = []
        for i, client in connection_list.items():
            try:
                client[0].send(task.encode('utf8'))
            except Exception:
                to_remove.append(i)
                print(f'Connection with id {i} closed')
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
        self.connection_process = Process(target=connection_function, args=(self.sock, self.connection_list))
        self.connection_process.daemon = True
        self.connection_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.connection_list, self.child_conn))
        self.send_process.daemon = True
        self.send_process.start()

        self.game = Game(Game.Side.SERVER, send_connection=self.parent_conn)
        self.camera = Camera(self.game)

        self.append_child(Minimap(self.game, self.camera))

    def update(self, event):
        self.camera.update(event)
        self.game.update(event)

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        for unit in self.game.sprites:
            unit.draw(screen, self.camera)
        self.camera.draw_center(screen)

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
