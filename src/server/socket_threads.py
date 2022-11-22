import json
import socket
from multiprocessing import Process
from multiprocessing.connection import Connection
from typing import Any

from src.server.types import Connections, ConnectionInfo, SocketId


def wait_for_new_connections(server_socket: socket.socket, connections: Connections,
                             received_actions: list[tuple[int, Any]]):
    next_id = 0
    while True:
        connection, address = server_socket.accept()
        send_process = Process(target=receive_data_from_socket,
                               args=(next_id, connection, received_actions, connections),
                               daemon=True)
        send_process.start()
        connections[next_id] = ConnectionInfo(connection, address[0], address[1], send_process.pid)

        print(f'Connection with id {next_id} opened')
        next_id += 1


def receive_data_from_socket(socket_id: int, connection: socket.socket, submit_list: list[tuple[int, Any]],
                             connections: Connections):
    command_buffer = ''
    while True:
        try:
            command_buffer += connection.recv(1024).decode('utf8')
        except Exception as ex:
            submit_list.append((socket_id, ['disconnected']))
            if socket_id is connections:
                connections.pop(socket_id)
            print(ex)
            print(f'Disconnected: {socket_id}')
            return

        splitter = command_buffer.find(';')
        while splitter != -1:
            command = command_buffer[:splitter]
            if command != '':
                submit_list.append((socket_id, json.loads(command)))
            command_buffer = command_buffer[splitter + 1:]
            splitter = command_buffer.find(';')


def send_to_player(connections: Connections, task: list, player_socket_id: SocketId):
    try:
        connections[player_socket_id].send_task(task)
    except KeyError:
        connections.pop(player_socket_id)
        print(f'No player with id: {player_socket_id}')


def send_to_all_players(connections: Connections, task: list):
    for socket_id, client in list(connections.items()):
        send_to_player(connections, task, socket_id)


def send_player_actions(connections: Connections, read_connection: Connection):
    while True:
        task, socket_id = read_connection.recv()
        if socket_id is not None:
            send_to_player(connections, task, socket_id)
        else:
            send_to_all_players(connections, task)
