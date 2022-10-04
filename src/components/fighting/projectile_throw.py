from dataclasses import dataclass


@dataclass(slots=True)
class ProjectileThrowComponent:
    delay: int
    projectile_name: str
    current_delay: int = 0
    arrow_speed: float = 2
