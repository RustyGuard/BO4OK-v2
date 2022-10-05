from dataclasses import dataclass


@dataclass
class ColliderComponent:
    radius: int
    static: bool = False
