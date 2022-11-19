import socket
from multiprocessing import Manager, Process, Pipe

from pygame.font import Font
from pygame.rect import Rect

from src.client.socket_threads import read_server_actions, send_function
from src.config import config
from src.core.types import PlayerInfo, ConnectedPlayer
from src.elements.pause_menu import PauseMenu
from src.elements.players_list import PlayersListElement
from src.main_loop_state import set_main_element
from src.menus.client.game_menu import ClientGameMenu
from src.ui import UIElement
from src.ui.fps_counter import FPSCounter
from src.ui.image import UIImage


class WaitForServerMenu(UIElement):
    def __init__(self, server_connection: socket, nick: str):
        super().__init__(config.screen.rect, None)
        fps_font = Font('assets/fonts/arial.ttf', 20)
        self.append_child(UIImage(self.bounds, 'assets/background/faded_background.png'))

        self.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))

        self.sock = server_connection

        manager = Manager()
        self.receive_list = manager.list()
        self.socket_process = Process(target=read_server_actions, args=(self.sock, self.receive_list))
        self.socket_process.start()

        self.parent_conn, self.child_conn = Pipe()
        self.send_process = Process(target=send_function, args=(self.sock, self.child_conn))
        self.send_process.daemon = True
        self.send_process.start()

        self.parent_conn.send(['nick', nick])

        self.connected_players: list[ConnectedPlayer] = []

        self.players_list_element = PlayersListElement(fps_font, self.connected_players)
        self.append_child(self.players_list_element)

        self.append_child(PauseMenu())

    def on_update(self):
        while self.receive_list:
            command, *args = self.receive_list.pop(0)
            print(command, args)
            if command == 'start':
                players = {int(i): j for i, j in args[1].items()}
                self.start(int(args[0]), players)
                return
            elif command == 'disconnect':
                from src.menus.main_menu import MainMenu
                set_main_element(MainMenu())
                return
            elif command == 'players':
                players, = args
                self.connected_players.clear()
                self.connected_players.extend(ConnectedPlayer(**player) for player in players)
                self.players_list_element.update_players()

    def start(self, team_id: int, players: dict[int, PlayerInfo]):
        set_main_element(
            ClientGameMenu(self.sock, self.receive_list, self.socket_process, self.parent_conn, self.child_conn,
                           self.send_process, players, team_id),
            shutdown_current_element=False)

    def shutdown(self):
        self.sock.close()
        self.send_process.terminate()
        self.socket_process.terminate()
        self.parent_conn.close()
        self.child_conn.close()
