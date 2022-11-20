import dataclasses
import random
import socket
from multiprocessing import Manager, Process, Pipe
from typing import Any

import pygame

from src.config import config
from src.constants import color_name_to_pygame_color, HOST_PLAYER_ID
from src.core.types import PlayerInfo, PlayerResources, ConnectedPlayer
from src.elements.pause_menu import PauseMenu
from src.elements.players_list import PlayersListElement
from src.main_loop_state import set_main_element
from src.menus.server.game_menu import ServerGameMenu
from src.server.socket_threads import Connections, wait_for_new_connections, send_player_actions
from src.ui import UIAnchor, UIElement
from src.ui.clickable_label import ClickableLabel
from src.ui.image import UIImage


class WaitForPlayersMenu(UIElement):
    def __init__(self, server_socket: socket.socket, local_player_nick: str):
        super().__init__()
        self.available_player_colors = list(color_name_to_pygame_color.keys())
        random.shuffle(self.available_player_colors)

        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.socket = server_socket
        self.local_player_nick = local_player_nick

        self.connected_players: list[ConnectedPlayer] = [
            ConnectedPlayer(HOST_PLAYER_ID, local_player_nick, self.available_player_colors.pop(), kickable=False)
        ]
        self.append_child(UIImage(image='assets/background/faded_background.png', size=config.screen.size))

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

        self.players_list_element = PlayersListElement(self.font, self.connected_players, self.kick_player)
        self.append_child(self.players_list_element)
        self.players_list_element.update_players()

        start_button = ClickableLabel(text='Начать', text_font=self.font,
                                      position=config.screen.rect.move(0, 100).center, size=(150, 75),
                                      anchor=UIAnchor.CENTER, on_click=self.start)
        self.append_child(start_button)

        self.append_child(PauseMenu())

    def update_player_list_for_clients(self):
        self.write_action_connection.send((['players', [dataclasses.asdict(player) for player in self.connected_players]], None))

    def kick_player(self, player: ConnectedPlayer):
        self.connected_players.remove(player)
        player_socket, address = self.connections.pop(player.socket_id)
        player_socket.shutdown(socket.SHUT_RDWR)
        player_socket.close()
        self.players_list_element.update_players()

    def clean_disconnected_players(self):
        for player in self.connected_players.copy():
            if player.socket_id not in self.connections and player.socket_id != HOST_PLAYER_ID:
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
            self.update_player_list_for_clients()
            self.players_list_element.update_players()

    def start(self):
        self.connection_process.terminate()

        players = self.get_players()

        for player in self.connected_players:
            if player.socket_id == HOST_PLAYER_ID:
                continue

            self.write_action_connection.send((['start', player.socket_id, players], player.socket_id))

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
            (connected_player.socket_id in self.connections or connected_player.socket_id == HOST_PLAYER_ID)}

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
    screen = config.screen.update_display_mode()

    host_ip = 'localhost:9090'

    host, port = host_ip.split(':')
    sock = socket.socket()
    sock.bind((host, int(port)))
    sock.listen()

    set_main_element(WaitForPlayersMenu(sock, 'Admin'))

    run_main_loop(screen)


if __name__ == '__main__':
    main()
