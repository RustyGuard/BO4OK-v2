from dataclasses import dataclass


@dataclass
class ArrowThrowComponent:
    delay: int
    current_delay: int = 0
    arrow_speed: float = 2
