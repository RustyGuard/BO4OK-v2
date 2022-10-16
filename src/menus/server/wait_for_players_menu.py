import random
import socket
from dataclasses import dataclass
from multiprocessing import Manager, Process, Pipe
from typing import Any

import pygame
from pygame import Color

from src.config import config
from src.constants import EVENT_UPDATE, color_name_to_pygame_color
from src.core.types import PlayerInfo, PlayerResources
from src.elements.pause_menu import PauseMenu
from src.main_loop_state import set_main_element
from src.menus.server.game_menu import ServerGameMenu
from src.server.socket_threads import Connections, wait_for_new_connections, send_player_actions
from src.ui import UIElement
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


@dataclass
class ConnectedPlayer:
    socket_id: int
    nick: str


class WaitForPlayersMenu(UIElement):
    PLAYER_AMOUNT_MASK = 'Подключено игроков {current_amount}/{required_amount}'

    def __init__(self, server_socket: socket.socket, required_player_amount: int, local_player_nick: str):
        super().__init__(config.screen.rect, None)

        self.socket = server_socket
        self.required_player_amount = required_player_amount
        self.local_player_nick = local_player_nick

        self.connected_players: list[ConnectedPlayer] = []
        self.append_child(UIImage(self.bounds, 'assets/data/faded_background.png'))

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

        self.font = pygame.font.SysFont('Comic Sans MS', 20)
        self.players_count = TextLabel(None, Color('white'), self.font,
                                       self.PLAYER_AMOUNT_MASK.format(current_amount=0,
                                                                      required_amount=self.required_player_amount),
                                       center=config.screen.rect.center)
        self.append_child(self.players_count)
        self.append_child(PauseMenu())

    def clean_disconnected_players(self):
        for player in self.connected_players.copy():
            if player.socket_id not in self.connections:
                self.connected_players.remove(player)

    def is_all_nicks_sent(self):
        connected_player_ids = {player.socket_id for player in self.connected_players}
        connected_sockets = set(self.connections.keys())

        return connected_player_ids == connected_sockets

    def update(self, event):
        super().update(event)
        if event.type == EVENT_UPDATE:
            while self.received_actions:
                sock_id, msg = self.received_actions.pop(0)
                print(msg)
                if msg[0] == 'nick':
                    self.connected_players.append(ConnectedPlayer(
                        socket_id=sock_id,
                        nick=msg[1]
                    ))
                self.clean_disconnected_players()
                if len(self.connections) >= self.required_player_amount and self.is_all_nicks_sent():
                    self.start()
                    return
            self.players_count.set_text(self.PLAYER_AMOUNT_MASK.format(current_amount=len(self.connections),
                                                                       required_amount=self.required_player_amount))

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
        colors = list(color_name_to_pygame_color.keys())
        random.shuffle(colors)

        players = {
            connected_player.socket_id:
                PlayerInfo(
                    color_name=colors.pop(),
                    socket_id=connected_player.socket_id,
                    nick=connected_player.nick,
                    resources=PlayerResources(
                        money=config.world.start_money,
                        wood=config.world.start_wood,
                        meat=config.world.start_meat,
                        max_meat=config.world.base_meat,
                    )
                ) for connected_player in self.connected_players if connected_player.socket_id in self.connections}

        players[-1] = PlayerInfo(  # Add host to game
            color_name=colors.pop(),
            socket_id=-1,
            nick=self.local_player_nick,
            resources=PlayerResources(
                money=config.world.start_money,
                wood=config.world.start_wood,
                meat=config.world.start_meat,
                max_meat=config.world.base_meat,
            )
        )
        return players

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

    set_main_element(WaitForPlayersMenu(sock))

    run_main_loop(screen)


if __name__ == '__main__':
    main()
