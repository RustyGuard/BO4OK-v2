from multiprocessing.connection import Connection


class ClientActionSender:
    def __init__(self, write_action_connection: Connection):
        self.write_action_connection = write_action_connection
