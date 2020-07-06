import socket
from multiprocessing import Process, Manager
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from constants import EVENT_UPDATE
from ui import UIElement, FPSCounter


def listen(sock: socket.socket, submit_list):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        submit_list.append(data.decode('utf8'))
    print('Disconnected')


class ClientGameWindow(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)

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

        self.pos = [50, 50]
        self.box_color = Color('black')

    def update(self, event):
        if event.type == EVENT_UPDATE:
            while self.receive_list:
                args = self.receive_list.pop(0).split('~')
                if args[0] == '1':
                    self.pos[0] = int(args[1])
                    self.pos[1] = int(args[2])
                elif args[0] == '2':
                    self.box_color.r = int(args[1])
                    self.box_color.g = int(args[2])
                    self.box_color.b = int(args[3])

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(screen, self.box_color, Rect(self.pos, (50, 50)))

    def shutdown(self):
        self.sock.close()
