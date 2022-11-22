import json
import socket
import subprocess
from dataclasses import dataclass

from src.utils.json_utils import PydanticEncoder


@dataclass(slots=True)
class ConnectionInfo:
    client_connection: socket.socket
    client_address: str
    client_port: int
    action_listener_pid: int

    def send_task(self, task: list):
        self.client_connection.send((json.dumps(task, cls=PydanticEncoder) + ';').encode('utf8'))

    def close(self):
        self.send_task(['disconnect'])
        self.client_connection.close()

        subprocess.run(f'taskkill /PID {self.action_listener_pid} /f', stdout=subprocess.DEVNULL)


SocketId = int

Connections = dict[SocketId, ConnectionInfo]
