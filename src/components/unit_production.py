from dataclasses import dataclass, field


@dataclass
class UnitProductionComponent:
    delay: int
    unit_queue: list[str] = field(default_factory=lambda: [])
    current_delay: int = 0
