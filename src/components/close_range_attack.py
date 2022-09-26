from dataclasses import dataclass


@dataclass
class CloseRangeAttack:
    delay: int
    damage: int
    current_delay: int = 0
