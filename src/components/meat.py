from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ReturnMeatOnDeath:
    meat_amount: int


@dataclass(slots=True)
class MaxMeatIncrease:
    meat_amount: int
    increased: bool = False
