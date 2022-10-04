from dataclasses import dataclass


@dataclass
class CloseRangeAttackComponent:
    delay: int
    damage: int
    current_delay: int = 0
