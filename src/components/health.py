from dataclasses import dataclass, field


@dataclass
class HealthComponent:
    max_amount: int
    amount: int = field(default=None)

    def __post_init__(self):
        if self.amount is None:
            self.amount = self.max_amount

    def apply_damage(self, damage: int):
        self.amount = max(0, self.amount - damage)
