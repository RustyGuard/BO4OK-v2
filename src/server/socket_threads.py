import json
import socket
from multiprocessing import Process
from multiprocessing.connection import Connection
from typing import Any

from src.utils.json_utils import PydanticEncoder

Connections = dict[int, tuple[socket.socket, Any]]


def wait_for_new_connections(socket: socket.socket, connections: Connections,
                             received_actions: list[tuple[int, Any]]):
    next_id = 0
    while True:
        conn, addr = socket.accept()
        connections[next_id] = (conn, addr)
        send_process = Process(target=receive_data_from_socket, args=(next_id, conn, received_actions, connections),
                               daemon=True)
        send_process.start()

        print(f'Connection with id {next_id} opened')
        next_id += 1


def receive_data_from_socket(socket_id: int, socket: socket.socket, submit_list: list[tuple[int, Any]],
                             connections: Connections):
    command_buffer = ''
    while True:
        try:
            command_buffer += socket.recv(1024).decode('utf8')
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


def send_player_actions(connections: Connections, read_connection: Connection):
    while True:
        task, socket_id = read_connection.recv()
        if socket_id is not None:
            try:
                connections[socket_id][0].send((json.dumps(task, cls=PydanticEncoder) + ';').encode('utf8'))
            except IndexError:
                print(f'No player with id: {socket_id}')
        else:
            for i, client in list(connections.items()):
                try:
                    client[0].send((json.dumps(task) + ';').encode('utf8'))
                except Exception as ex:
                    connections.pop(i)
                    print(f'Connection with id {i} closed, because of {ex}')
