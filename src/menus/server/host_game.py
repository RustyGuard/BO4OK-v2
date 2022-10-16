import socket

import pygame
from pygame import Color, Rect

from src.config import config
from src.main_loop_state import set_main_element
from src.menus.server.wait_for_players_menu import WaitForPlayersMenu
from src.ui import UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.input import UIInput
from src.ui.text_label import TextLabel


class HostGame(UIElement):
    def __init__(self):
        super().__init__(config.screen.rect)
        font = pygame.font.SysFont('Comic Sans MS', 20)

        self.background = UIImage(self.bounds, 'assets/data/faded_background.png')
        self.append_child(self.background)

        header = TextLabel(None, font=font, color=Color('white'), text='Создание сервера')
        self.append_child(header)
        header.bounds.center = config.screen.rect.move(0, -250).center

        nick_label = TextLabel(None, font=font, color=Color('white'), text='Ваш ник: ',
                               center=config.screen.rect.move(-150, -150).center)
        self.append_child(nick_label)

        self.nick_input = UIInput(Rect(0, 0, 300, 50), Color('white'), Color('grey'), font,
                                  center=config.screen.rect.move(150, -150).center, limit=20, focused=True)
        self.append_child(self.nick_input)

        host_label = TextLabel(None, font=font, color=Color('white'), text='Хост: ',
                               center=config.screen.rect.move(-150, -95).center)
        self.append_child(host_label)

        self.host_input = UIInput(Rect(0, 0, 300, 50), Color('white'), Color('grey'), font,
                                  center=config.screen.rect.move(150, -95).center, limit=20)
        self.append_child(self.host_input)

        players_label = TextLabel(None, font=font, color=Color('white'), text='Количество игроков: ',
                                  center=config.screen.rect.move(-150, -40).center)
        self.append_child(players_label)

        self.players_input = UIInput(Rect(0, 0, 300, 50), Color('white'), Color('grey'), font,
                                     center=config.screen.rect.move(150, -40).center, limit=20)
        self.append_child(self.players_input)

        connect_button = ClickableLabel(Rect((0, 0), (150, 75)), self.connect, 'Создать', font,
                                        center=config.screen.rect.move(0, 15).center)
        self.append_child(connect_button)

    def connect(self):
        if self.nick_input.value == '':
            return

        host_ip = self.host_input.value or 'localhost:9090'

        host, port = host_ip.split(':')
        sock = socket.socket()
        sock.bind((host, int(port)))
        try:
            sock.listen(1)
        except ConnectionRefusedError:
            print('Not connected')
            return

        players_amount = int(self.players_input.value or '1')
        set_main_element(WaitForPlayersMenu(sock, required_player_amount=players_amount, nick=self.nick_input.value))
