import socket
from multiprocessing import Process, Manager
from typing import Optional

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from config import config
from constants import EVENT_UPDATE
from ui import UIElement, FPSCounter
from core import Game, Camera, Unit, Minimap


def listen(sock: socket.socket, submit_list):
    while True:
        try:
            data = sock.recv(1024)
        except Exception as ex:
            print(ex)
            return
        if not data:
            break
        submit_list.append(data.decode('utf8'))
    print('Disconnected')


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

        self.game = Game(Game.Side.CLIENT)
        self.camera = Camera(self.game)

        self.minimap = Minimap(self.game, self.camera)

        self.append_child(self.minimap)

    def update(self, event):
        self.game.update(event)
        self.camera.update(event)

        if event.type == EVENT_UPDATE:
            while self.receive_list:
                args = self.receive_list.pop(0).split('~')
                self.game.handle_command(args[0], args[1:])

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        for spr in self.game.sprites:
            spr.draw(screen, self.camera)
        self.camera.draw_center(screen)

    def shutdown(self):
        self.socket_process.terminate()
        self.sock.close()
