from dataclasses import dataclass


@dataclass(slots=True)
class PlayerOwnerComponent:
    color_name: str
    nick: str
    socket_id: int
