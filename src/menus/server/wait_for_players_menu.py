import random
import socket
from dataclasses import dataclass
from functools import partial
from multiprocessing import Manager, Process, Pipe
from typing import Any

import pygame
from pygame import Color, Rect

from src.config import config
from src.constants import EVENT_UPDATE, color_name_to_pygame_color
from src.core.types import PlayerInfo, PlayerResources
from src.elements.pause_menu import PauseMenu
from src.main_loop_state import set_main_element
from src.menus.server.game_menu import ServerGameMenu
from src.server.socket_threads import Connections, wait_for_new_connections, send_player_actions
from src.ui import UIElement
from src.ui.button import UIButton
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


@dataclass
class ConnectedPlayer:
    socket_id: int
    nick: str
    color_name: str
    kickable: bool = True

    @property
    def color(self):
        return color_name_to_pygame_color[self.color_name]


class WaitForPlayersMenu(UIElement):
    PLAYER_AMOUNT_MASK = 'Подключено игроков: {current_amount}'
    ADMIN_SOCKET_ID = -1

    def __init__(self, server_socket: socket.socket, local_player_nick: str):
        super().__init__(config.screen.rect, None)
        self.available_player_colors = list(color_name_to_pygame_color.keys())
        random.shuffle(self.available_player_colors)

        self.font = pygame.font.SysFont('Comic Sans MS', 20)

        self.socket = server_socket
        self.local_player_nick = local_player_nick

        self.connected_players: list[ConnectedPlayer] = [
            ConnectedPlayer(self.ADMIN_SOCKET_ID, 'Вы', self.available_player_colors.pop(), kickable=False)
        ]
        self.append_child(UIImage(self.bounds, 'assets/background/faded_background.png'))

        manager = Manager()
        self.manager = manager
        self.connections: Connections = manager.dict()
        self.received_actions: list[tuple[int, Any]] = manager.list()

        self.connection_process = Process(target=wait_for_new_connections, args=(self.socket, self.connections,
                                                                                 self.received_actions))
        self.connection_process.start()

        self.write_action_connection, self.read_connection = Pipe()
        self.send_process = Process(target=send_player_actions, args=(self.connections, self.read_connection),
                                    daemon=True)
        self.send_process.start()

        self.players_count = TextLabel(None, Color('white'), self.font,
                                       self.PLAYER_AMOUNT_MASK.format(current_amount=1),
                                       center=config.screen.rect.move(0, -175).center)
        self.append_child(self.players_count)

        self.players_list_element = UIElement()
        self.append_child(self.players_list_element)
        self.update_players_list()

        start_button = ClickableLabel(Rect((0, 0), (150, 75)), self.start, 'Начать', self.font,
                                      center=config.screen.rect.move(0, 100).center)
        self.append_child(start_button)

        self.append_child(PauseMenu())

    def update_players_list(self):
        self.players_count.set_text(self.PLAYER_AMOUNT_MASK.format(current_amount=len(self.connected_players)))

        self.players_list_element.children.clear()
        offset_y = -125
        for i, player in enumerate(self.connected_players):
            player_box = UIElement(Rect(0, 0, 500, 30), Color('gray'),
                                   center=config.screen.rect.move(0, offset_y + i * 35).center)
            self.players_list_element.append_child(player_box)
            self.players_list_element.append_child(
                UIElement(Rect((0, 0), (24, 24)), color=player.color, border_width=1,
                          center=player_box.bounds.move(15, 0).midleft))
            self.players_list_element.append_child(
                TextLabel(Rect(0, 0, 400, 25), Color('black'), self.font, player.nick,
                          center=config.screen.rect.move(0, offset_y - 2 + i * 35).center))

            if player.kickable:
                remove_button = UIButton(Rect((0, 0), (24, 24)), None, partial(self.kick_player, player),
                                         center=player_box.bounds.move(-15, 0).midright)
                self.players_list_element.append_child(remove_button)
                self.players_list_element.append_child(UIImage(remove_button.bounds.copy(), 'assets/ui/cross.png'))
                remove_button.on_mouse_hover = partial(remove_button.set_color, Color('darkred'))
                remove_button.on_mouse_exit = partial(remove_button.set_color, None)

    def kick_player(self, player: ConnectedPlayer):
        self.connected_players.remove(player)
        player_socket, address = self.connections.pop(player.socket_id)
        player_socket.shutdown(socket.SHUT_RDWR)
        player_socket.close()
        self.update_players_list()

    def clean_disconnected_players(self):
        for player in self.connected_players.copy():
            if player.socket_id not in self.connections and player.socket_id != self.ADMIN_SOCKET_ID:
                self.connected_players.remove(player)

    def on_second_passed(self):
        self.clean_disconnected_players()

    def on_update(self):
        while self.received_actions:
            sock_id, msg = self.received_actions.pop(0)
            if msg[0] == 'nick':
                self.connected_players.append(ConnectedPlayer(
                    socket_id=sock_id,
                    nick=msg[1],
                    color_name=self.available_player_colors.pop(),
                ))
            self.clean_disconnected_players()
            self.update_players_list()

    def start(self):
        self.connection_process.terminate()

        players = self.get_players()

        for socket_id in self.connections:
            self.write_action_connection.send((['start', socket_id, players], socket_id))

        set_main_element(
            ServerGameMenu(self.socket, self.connections, self.received_actions, self.write_action_connection,
                           self.send_process, players),
            shutdown_current_element=False)

    def get_players(self) -> dict[int, PlayerInfo]:
        return {
            connected_player.socket_id:
                PlayerInfo(
                    color_name=connected_player.color_name,
                    socket_id=connected_player.socket_id,
                    nick=connected_player.nick,
                    resources=PlayerResources(
                        money=config.world.start_money,
                        wood=config.world.start_wood,
                        meat=config.world.start_meat,
                        max_meat=config.world.base_meat,
                    )
                ) for connected_player in self.connected_players if
            (connected_player.socket_id in self.connections or connected_player.socket_id == self.ADMIN_SOCKET_ID)}

    def shutdown(self):
        self.connection_process.terminate()
        self.send_process.terminate()

        self.write_action_connection.close()
        self.socket.close()
        self.manager.shutdown()


def main():
    import pygame

    from src.config import config
    from src.main import run_main_loop
    from src.main_loop_state import set_main_element

    pygame.init()
    screen = pygame.display.set_mode(config.screen.size)

    host_ip = 'localhost:9090'

    host, port = host_ip.split(':')
    sock = socket.socket()
    sock.bind((host, int(port)))
    sock.listen()

    set_main_element(WaitForPlayersMenu(sock, 'Admin'))

    run_main_loop(screen)


if __name__ == '__main__':
    main()
