import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.core.types import PlayerInfo, RequiredCost
from src.ui import UIElement
from src.ui.text_label import TextLabel


class ResourceDisplayMenu(UIElement):
    COST_OFFSET = -32

    def __init__(self, player: PlayerInfo, bounds: Rect, big_font: Font, small_font: Font):
        super().__init__()
        self._big_font = big_font
        self._small_font = small_font
        self._money_count = TextLabel(text='-', text_color=Color('yellow'), font=big_font, position=bounds.move(0, 0).topleft)
        self.append_child(self._money_count)
        self._wood_count = TextLabel(text='-', text_color=Color('brown'), font=big_font, position=bounds.move(105, 0).topleft)
        self.append_child(self._wood_count)
        self._meat_count = TextLabel(text='-/-', text_color=Color('pink'), font=big_font, position=bounds.move(220, 0).topleft)
        self.append_child(self._meat_count)

        self._cost_display = UIElement()
        self.append_child(self._cost_display)

        self.money_cost = TextLabel(text='-', text_color=Color('black'), font=big_font, position=bounds.move(0, self.COST_OFFSET).topleft)
        self._cost_display.append_child(self.money_cost)
        self.wood_cost = TextLabel(text='', text_color=Color('black'), font=big_font, position=bounds.move(105, self.COST_OFFSET).topleft)
        self._cost_display.append_child(self.wood_cost)
        self.meat_cost = TextLabel(text='', text_color=Color('black'), font=big_font, position=bounds.move(220, self.COST_OFFSET).topleft)
        self._cost_display.append_child(self.meat_cost)

        self._cost_display.enabled = False

        self._player = player
        self._cost: RequiredCost | None = None

        self.update_values()

    def display_cost(self, cost: RequiredCost):
        self._cost = cost
        self._cost_display.enabled = True

        self.money_cost.set_text(f'-{self._cost.money}' if self._cost.money else '')
        self.wood_cost.set_text(f'-{self._cost.wood}' if self._cost.wood else '')
        self.meat_cost.set_text(f'+{self._cost.meat}' if self._cost.meat else '')

        if not self._player.has_enough(cost):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
        self.update_values()

    def hide_cost(self, cost: RequiredCost):
        if self._cost == cost:
            self._cost = None
            self._cost_display.enabled = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.update_values()

    def update(self, event: pygame.event) -> bool:
        if super().update(event):
            return True

        return False

    def update_values(self) -> None:
        fields = (
            ('money', '_money_count', 'yellow', '{0}', -1),
            ('wood', '_wood_count', 'brown', '{0}', -1),
            ('meat', '_meat_count', 'pink', f'{{0}}/{self._player.resources.max_meat}', 1),
        )
        for field_name, text_field_name, field_color, field_format, field_multiplier in fields:
            text_field: TextLabel = getattr(self, text_field_name)
            current_amount = getattr(self._player.resources, field_name)
            if getattr(self._cost, field_name, False):
                color = Color('red')
                text = field_format.format(current_amount + field_multiplier * getattr(self._cost, field_name))
            else:
                color = Color(field_color)
                text = field_format.format(current_amount)
            text_field.set_text_color(color)
            text_field.set_text(text)
            if len(text) > 6:
                text_field.set_font(self._small_font)
            else:
                text_field.set_font(self._big_font)

        if self._cost and not self._player.has_enough(self._cost):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
