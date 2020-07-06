import random
import socket
from multiprocessing import Process, Manager, Pipe
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from constants import SCREEN_SIZE, EVENT_UPDATE
from main import Main
from ui import UIElement, FPSCounter


def connection_function(sock: socket.socket, connection_list):
    next_id = 0
    while True:
        conn, addr = sock.accept()
        connection_list[next_id] = (conn, addr)
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
        self.connection_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.connection_list, self.child_conn))
        self.send_process.start()

        self.box = Rect(50, 50, 50, 50)
        self.box_color = Color('blue')
        self.colors = ['aquamarine', 'cornflowerblue', 'cornsilk', 'chartreuse', 'coral']
        self.velocity = [2, 2]

    def update(self, event):
        if event.type == EVENT_UPDATE:
            self.box.move_ip(*self.velocity)
            if self.box.right >= self.relative_bounds.right or self.box.left <= self.relative_bounds.left:
                self.velocity[0] = -self.velocity[0]
                self.box_color = Color(random.choice(self.colors))
                self.parent_conn.send(f'2~{self.box_color.r}~{self.box_color.g}~{self.box_color.b}')
            if self.box.bottom >= self.relative_bounds.bottom or self.box.top <= self.relative_bounds.top:
                self.velocity[1] = -self.velocity[1]
                self.box_color = Color(random.choice(self.colors))
                self.parent_conn.send(f'2~{self.box_color.r}~{self.box_color.g}~{self.box_color.b}')

            self.parent_conn.send(f'1~{self.box.x}~{self.box.y}')

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(screen, self.box_color, self.box)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    elem = ServerGameWindow(Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]), Color('bisque'))

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
