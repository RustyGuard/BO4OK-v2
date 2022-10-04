from dataclasses import dataclass


@dataclass
class ResourceGathererComponent:
    delay: int
    gathering_speed: int

    max_wood_carried: int
    max_money_carried: int

    current_delay: int = 0

    wood_carried: int = 0
    money_carried: int = 0

    @property
    def is_backpack_full(self):
        return self.wood_carried >= self.max_wood_carried or self.money_carried >= self.max_money_carried