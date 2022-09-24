from dataclasses import dataclass, field

from src.core.types import RequiredCost, PlayerInfo


@dataclass(slots=True)
class UnitProductionComponent:
    delay: int
    producible_units: dict[str, RequiredCost]
    unit_queue: list[str] = field(default_factory=lambda: [])
    current_delay: int = 0

    def add_to_queue(self, unit_name: str, player: PlayerInfo) -> bool:
        if unit_name not in self.producible_units:
            print('This unit is not producible')
            return False

        cost = self.producible_units[unit_name]
        if not player.has_enough(cost):
            print('Player has not enough resources')
            return False

        player.spend(cost)
        self.unit_queue.append(unit_name)
        return True

    def assemble_on_client(self, _):
        self.producible_units = {unit_name: RequiredCost(**cost_dict) for unit_name, cost_dict in
                                 self.producible_units.items()}
