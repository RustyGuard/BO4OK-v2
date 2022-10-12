import random
import socket
from dataclasses import dataclass
from multiprocessing import Manager, Process, Pipe
from typing import Any

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.config import config
from src.constants import EVENT_UPDATE, color_name_to_pygame_color
from src.core.types import PlayerInfo, PlayerResources
from src.elements.pause_menu import PauseMenu
from src.main_loop_state import set_main_element
from src.menus.server.game_menu import ServerGameMenu
from src.server.server import Connections, wait_for_new_connections, send_player_actions
from src.ui import UIElement
from src.ui.fps_counter import FPSCounter


@dataclass
class ConnectedPlayer:
    socket_id: int
    nick: str


class WaitForPlayersMenu(UIElement):
    REQUIRED_AMOUNT_OF_PLAYERS = 1

    def __init__(self):
        super().__init__(config.screen.get_rect(), Color('bisque'))
        self.connected_players: list[ConnectedPlayer] = []
        fps_font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))

        self.socket = socket.socket()
        self.socket.bind((config.server.ip, config.server.port))
        self.socket.listen(1)

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
        self.append_child(PauseMenu())

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
                if len(self.connections) >= self.REQUIRED_AMOUNT_OF_PLAYERS and self.is_all_nicks_sent():
                    self.start()
                    return

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
                ) for connected_player in self.connected_players}

        players[-1] = PlayerInfo(  # Add host to game
            socket_id=-1,
            color_name='black',
            nick='Admin',
            resources=PlayerResources(
                money=50000,
                wood=50000,

                meat=0,
                max_meat=50000
            )
        )
        return players

    def shutdown(self):
        print('dsadjasjkdhakjdhs')
        self.connection_process.terminate()
        self.send_process.terminate()

        self.write_action_connection.close()
        self.socket.close()
        self.manager.shutdown()