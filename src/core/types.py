from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Type

from pydantic import BaseModel
from pygame import Color

from src.constants import color_name_to_pygame_color, SoundCode
from src.sound_player import play_sound


@dataclass
class RequiredCost:
    money: int = 0
    wood: int = 0
    meat: int = 0


class PlayerResources(BaseModel):
    wood: int
    money: int
    meat: int
    max_meat: int


class PlayerState(IntEnum):
    BATTLER = 0
    SPECTATOR = 1
    WINNER = 2


class PlayerInfo(BaseModel):
    socket_id: int
    color_name: str
    nick: str

    resources: PlayerResources

    current_state: PlayerState = PlayerState.BATTLER

    @property
    def color(self) -> Color:
        return color_name_to_pygame_color[self.color_name]

    def has_enough(self, cost: RequiredCost) -> bool:
        if self.current_state == PlayerState.SPECTATOR:
            return False

        return (
                self.resources.money >= cost.money and
                self.resources.wood >= cost.wood and
                (cost.meat == 0 or self.resources.meat + cost.meat <= self.resources.max_meat)
        )

    def play_not_enough_sound(self, cost: RequiredCost):
        if self.resources.money < cost.money:
            play_sound(SoundCode.GOLD_REQUIRED)
            return
        if self.resources.wood < cost.wood:
            play_sound(SoundCode.WOOD_REQUIRED)
            return
        if self.resources.meat + cost.meat > self.resources.max_meat:
            play_sound(SoundCode.MEAT_REQUIRED)
            return

    def spend(self, cost: RequiredCost):
        self.resources.money -= cost.money
        self.resources.wood -= cost.wood
        self.resources.meat += cost.meat


EntityId = str
Component = object


@dataclass
class StoredSystem:
    variables: dict[str, Any]
    components: dict[str, Type[Component]]  # key is argument name
    has_entity_id_argument: bool
    has_ecs_argument: bool
