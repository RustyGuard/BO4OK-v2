import json
import socket
from multiprocessing.connection import Connection

from src.utils.json_utils import PydanticDecoder


def read_server_actions(socket: socket.socket, submit_list: list[list]):
    command_buffer = ''
    while True:
        try:
            command_buffer += socket.recv(1024).decode('utf8')

        except Exception as ex:
            submit_list.append(['disconnect'])
            print(ex)
            print('Disconnected')
            return

        if command_buffer == '':
            submit_list.append(['disconnect'])
            print('Disconnected')
            return

        splitter = command_buffer.find(';')
        while splitter != -1:
            command = command_buffer[:splitter]
            if command != '':
                submit_list.append(json.loads(command, cls=PydanticDecoder))
            command_buffer = command_buffer[splitter + 1:]
            splitter = command_buffer.find(';')



def send_function(sock: socket.socket, read_connection: Connection):
    while True:
        task = read_connection.recv()
        try:
            sock.send((json.dumps(task) + ';').encode('utf8'))
        except Exception as ex:
            print(f'Connection closed, because of {ex}')
            return
