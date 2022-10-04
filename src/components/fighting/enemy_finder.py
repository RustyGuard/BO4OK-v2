from dataclasses import dataclass


@dataclass
class EnemyFinderComponent:
    anger_range: float
    delay: int = 0
