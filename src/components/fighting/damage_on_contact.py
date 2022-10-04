from dataclasses import dataclass


@dataclass
class DamageOnContactComponent:
    damage: int
    die_on_contact: bool = True
    check_delay: int = 0
