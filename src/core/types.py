from pydantic import BaseModel, validator
from pygame import Color

from src.constants import color_name_to_pygame_color


class RequiredCost(BaseModel):
    money: int = 0
    wood: int = 0

    @validator('money', 'wood')
    def validate_positive(cls, v):
        assert v >= 0
        return v


class PlayerResources(BaseModel):
    wood: int
    money: int
    meat: int
    max_meat: int


class PlayerInfo(BaseModel):
    team_id: int
    color_name: str
    nick: str

    resources: PlayerResources

    @property
    def color(self) -> Color:
        return color_name_to_pygame_color[self.color_name]

    def has_enough(self, cost: RequiredCost) -> bool:
        return self.resources.money >= cost.money and self.resources.wood >= cost.wood

    def spend(self, cost: RequiredCost):
        self.resources.money -= cost.money
        self.resources.wood -= cost.wood
