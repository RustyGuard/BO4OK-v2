import socket

import pygame
from pygame import Color

from src.config import config
from src.main_loop_state import set_main_element
from src.menus.server.wait_for_players_menu import WaitForPlayersMenu
from src.ui import UIAnchor, UIElement, UIButton
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.input import UIInput
from src.ui.text_label import TextLabel


class HostGame(UIElement):
    def __init__(self):
        super().__init__()
        font = pygame.font.SysFont('Comic Sans MS', 30)

        self.background = UIImage(image='assets/background/faded_background.png', size=config.screen.size)
        self.append_child(self.background)

        header = TextLabel(text='Создание сервера', text_color=Color('white'), font=font,
                           position=config.screen.rect.move(0, -250).center, anchor=UIAnchor.CENTER)
        self.append_child(header)

        nick_label = TextLabel(text='Ваш ник: ', text_color=Color('white'), font=font,
                               position=config.screen.rect.move(-150, -150).center, anchor=UIAnchor.CENTER)
        self.append_child(nick_label)

        self.nick_input = UIInput(position=config.screen.rect.move(150, -150).center,
                                  size=(300, 50),
                                  anchor=UIAnchor.CENTER,
                                  text_color=Color('white'),
                                  background_color=Color('grey'),
                                  font=font,
                                  max_length=20,
                                  focused=True)
        self.append_child(self.nick_input)

        host_label = TextLabel(text='Хост: ', text_color=Color('white'), font=font,
                               position=config.screen.rect.move(-150, -95).center, anchor=UIAnchor.CENTER)
        self.append_child(host_label)

        self.host_input = UIInput(position=config.screen.rect.move(150, -95).center,
                                  size=(300, 50),
                                  anchor=UIAnchor.CENTER,
                                  text_color=Color('white'),
                                  background_color=Color('grey'),
                                  font=font,
                                  max_length=20)
        self.append_child(self.host_input)

        connect_button = ClickableLabel(text='Создать', text_font=font, position=config.screen.rect.move(0, 15).center,
                                        size=(150, 75), anchor=UIAnchor.CENTER, on_click=self.connect)
        self.append_child(connect_button)

        back_button = UIButton(position=(5, 5), size=(75, 75), on_click=self.go_back)
        back_button.append_child(UIImage(image='assets/ui/left-arrow.png',
                                         position=back_button._bounds.topleft,
                                         size=back_button._bounds.size))
        self.append_child(back_button)

    def go_back(self):
        from src.menus.main_menu import MainMenu
        set_main_element(MainMenu())

    def connect(self):
        if self.nick_input.value == '':
            return

        host_ip = self.host_input.value or 'localhost:9090'

        try:
            host, port = host_ip.split(':')
            port = int(port)
        except TypeError:
            host, port = host_ip, 9090
        except ValueError:
            print(f'Can not parse port of {host_ip}')
            return

        sock = socket.socket()
        try:
            sock.bind((host, port))
        except socket.gaierror:
            print(f'Not connected to {host_ip}')
            return

        try:
            sock.listen()
        except ConnectionRefusedError:
            print(f'Not connected to {host_ip}')
            return

        set_main_element(WaitForPlayersMenu(sock,
                                            local_player_nick=self.nick_input.value))
