from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PlayerOwnerComponent:
    color_name: str
    nick: str
    socket_id: int
