import json
import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from signal import Signals

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
        try:
            self.send_task(['disconnect'])
        except ConnectionResetError:
            pass
        self.client_connection.close()

        if sys.platform == 'win32':
            subprocess.run(f'taskkill /PID {self.action_listener_pid} /f', stdout=subprocess.DEVNULL)
        elif sys.platform == 'linux':
            os.kill(self.action_listener_pid, Signals.SIGKILL)


SocketId = int

Connections = dict[SocketId, ConnectionInfo]
