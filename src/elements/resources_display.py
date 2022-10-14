import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.core.types import PlayerInfo, RequiredCost
from src.ui.text_label import TextLabel
from src.ui import UIElement


class ResourceDisplayMenu(UIElement):
    COST_OFFSET = -32

    def __init__(self, player: PlayerInfo, bounds: Rect, font: Font):
        super().__init__(bounds, None)
        self.money_count = TextLabel(Rect(bounds.topleft, (500, 500)), Color('yellow'), font, '-')
        self.append_child(self.money_count)
        self.wood_count = TextLabel(Rect(bounds.move(105, 0).topleft, (500, 500)), Color('brown'), font, '-')
        self.append_child(self.wood_count)
        self.meat_count = TextLabel(Rect(bounds.move(220, 0).topleft, (500, 500)), Color('pink'), font, '-/-')
        self.append_child(self.meat_count)

        self.cost_display = UIElement()
        self.append_child(self.cost_display)

        self.money_cost = TextLabel(Rect(bounds.move(0, self.COST_OFFSET).topleft, (500, 500)), Color('black'), font, '-')
        self.cost_display.append_child(self.money_cost)
        self.wood_cost = TextLabel(Rect(bounds.move(105, self.COST_OFFSET).topleft, (500, 500)), Color('black'), font, '')
        self.cost_display.append_child(self.wood_cost)
        self.meat_cost = TextLabel(Rect(bounds.move(220, self.COST_OFFSET).topleft, (500, 500)), Color('black'), font, '')
        self.cost_display.append_child(self.meat_cost)

        self.cost_display.enabled = False

        self.player = player
        self.cost: RequiredCost | None = None

        self.update_values()

    def display_cost(self, cost: RequiredCost):
        self.cost = cost
        self.cost_display.enabled = True

        self.money_cost.set_text(f'-{self.cost.money}' if self.cost.money else '')
        self.wood_cost.set_text(f'-{self.cost.wood}' if self.cost.wood else '')
        self.meat_cost.set_text(f'+{self.cost.meat}' if self.cost.meat else '')

        if not self.player.has_enough(cost):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
        self.update_values()

    def hide_cost(self, cost: RequiredCost):
        if self.cost == cost:
            self.cost = None
            self.cost_display.enabled = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.update_values()

    def update(self, event: pygame.event) -> bool:
        if super().update(event):
            return True

        return False

    def update_values(self) -> None:
        self.money_count.set_color(Color('yellow'))
        self.wood_count.set_color(Color('brown'))
        self.meat_count.set_color(Color('pink'))

        if self.cost:
            if self.cost.money:
                self.money_count.set_color(Color('red'))
            if self.cost.wood:
                self.wood_count.set_color(Color('red'))
            if self.cost.meat:
                self.meat_count.set_color(Color('red'))

            self.money_count.set_text(f'{self.player.resources.money - self.cost.money}')
            self.wood_count.set_text(f'{self.player.resources.wood - self.cost.wood}')
            self.meat_count.set_text(f'{self.player.resources.meat + self.cost.meat}/{self.player.resources.max_meat}')

            if not self.player.has_enough(self.cost):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
        else:
            self.money_count.set_text(f'{self.player.resources.money}')
            self.wood_count.set_text(f'{self.player.resources.wood}')
            self.meat_count.set_text(f'{self.player.resources.meat}/{self.player.resources.max_meat}')
