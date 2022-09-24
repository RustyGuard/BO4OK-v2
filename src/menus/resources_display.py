import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.constants import EVENT_UPDATE
from src.core.types import PlayerInfo, RequiredCost
from src.ui import UIElement, Label


class ResourceDisplayMenu(UIElement):
    def __init__(self, player: PlayerInfo, bounds: Rect, font: Font):
        super().__init__(bounds, None)
        self.money_count = Label(Rect(0, 0, 500, 500), Color('yellow'), font, '-')
        self.append_child(self.money_count)
        self.wood_count = Label(Rect(105, 0, 500, 500), Color('brown'), font, '-')
        self.append_child(self.wood_count)
        self.meat_count = Label(Rect(220, 0, 500, 500), Color('pink'), font, '-/-')
        self.append_child(self.meat_count)

        self.cost_display = UIElement(Rect(0, -32, 0, 0), None)
        self.append_child(self.cost_display)

        self.money_cost = Label(Rect(0, 0, 500, 500), Color('black'), font, '-')
        self.cost_display.append_child(self.money_cost)
        self.wood_cost = Label(Rect(105, 0, 500, 500), Color('black'), font, '')
        self.cost_display.append_child(self.wood_cost)
        self.meat_cost = Label(Rect(220, 0, 500, 500), Color('black'), font, '')
        self.cost_display.append_child(self.meat_cost)

        self.cost_display.enabled = False

        self.player = player
        self.cost: RequiredCost | None = None

    def display_cost(self, cost: RequiredCost):
        self.cost = cost
        self.cost_display.enabled = True

        self.money_cost.set_text(f'-{self.cost.money}' if self.cost.money else '')
        self.wood_cost.set_text(f'-{self.cost.wood}' if self.cost.wood else '')
        self.meat_cost.set_text(f'+{self.cost.meat}' if self.cost.meat else '')

    def hide_cost(self, cost: RequiredCost):
        if self.cost == cost:
            self.cost = None
            self.cost_display.enabled = False

    def update(self, event: pygame.event) -> bool:
        if super().update(event):
            return True
        if event.type == EVENT_UPDATE:
            self.update_values()
        return False

    def update_values(self) -> None:
        self.money_count.set_color(Color('yellow'))
        self.wood_count.set_color(Color('brown'))
        self.meat_count.set_color(Color('pink'))

        if self.cost:
            if self.cost.money:
                self.money_count.set_text(f'{self.player.resources.money - self.cost.money}')
                self.money_count.set_color(Color('red'))
            if self.cost.wood:
                self.wood_count.set_text(f'{self.player.resources.wood - self.cost.wood}')
                self.wood_count.set_color(Color('red'))
            if self.cost.meat:
                self.meat_count.set_text(
                    f'{self.player.resources.meat + self.cost.meat}/{self.player.resources.max_meat}')
                self.meat_count.set_color(Color('red'))
        else:
            self.money_count.set_text(f'{self.player.resources.money}')
            self.wood_count.set_text(f'{self.player.resources.wood}')
            self.meat_count.set_text(f'{self.player.resources.meat}/{self.player.resources.max_meat}')
