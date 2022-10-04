from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ReturnMeatOnDeathComponent:
    meat_amount: int


@dataclass(slots=True)
class MaxMeatIncreaseComponent:
    meat_amount: int
    increased: bool = False
