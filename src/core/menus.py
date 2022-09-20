import random

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.core.game import Game
from src.core.types import PlayerInfo
from src.entities.units_base import ProducingBuilding
from src.ui import UIElement, UIButton, UIImage, Label


class BuildMenu(UIElement):
    class BuildMenuItem:
        def __init__(self, name, entity_json, game):
            self.entity_json = entity_json
            self.game = game
            self.name = name
            self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            self.icon = pygame.image.load(self.entity_json['icon'].format(team=self.game.current_player.color_name))

    def __init__(self, bounds, game):
        super().__init__(bounds, None)
        self.selected = None
        self.game = game
        self.buildings = {}
        i = 0
        for name, entity in self.game.mod_loader.entities.items():
            if 'buildable' in entity['tags']:
                self.buildings[name] = BuildMenu.BuildMenuItem(name, entity, game)
                btn = UIButton(Rect(0, i * 55 + 15, 50, 50), None, self.select, name)
                btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, self.buildings[name].icon))
                self.append_child(btn)
                i += 1

    def draw(self, screen) -> None:
        if self.selected:
            r = self.selected.icon.get_rect()
            r.center = pygame.mouse.get_pos()
            screen.blit(self.selected.icon, r)
        super().draw(screen)

    def update(self, event) -> bool:
        if super().update(event):
            return True
        if self.selected:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.game.place_building(self.selected.name, pygame.mouse.get_pos())
                    return True
                if event.button == 3:
                    self.selected = None
                    return True
        return False

    def select(self, item_id):
        self.selected = self.buildings[item_id] if (item_id is not None) else None


class ProduceMenu(UIElement):
    class ProduceMenuItem:
        def __init__(self, name: str, entity_json, game: Game):
            self.entity_json = entity_json
            self.game = game
            self.name = name
            self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            self.icon = pygame.image.load(self.entity_json['icon'].format(team=self.game.current_player.color_name))

    def __init__(self, bounds, game):
        super().__init__(bounds, None)
        self.game = game
        self.units = {}

    def set_selected(self, unit):
        self.childs.clear()
        for i, name in enumerate(unit.cls_dict['valid_types']):
            entity = self.game.mod_loader.entities[name]
            self.units[name] = ProduceMenu.ProduceMenuItem(name, entity, self.game)
            btn = UIButton(Rect(150, i * 30 + 15, 25, 25), None, self.select, name)
            btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, self.units[name].icon))

            self.append_child(btn)
        self.selected_unit = unit.unit_id

    def select(self, name) -> None:
        self.game.send([Game.ServerCommands.PRODUCE_UNIT, self.selected_unit, name])

    def draw(self, screen) -> None:
        super().draw(screen)

    def update(self, event) -> None:
        if super().update(event):
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            collide = self.game.collide_cursor(event.pos)
            for unit in collide:
                if isinstance(unit, ProducingBuilding) and unit.team == self.game.current_team:
                    self.set_selected(unit)
                    break
        return False


class ResourceMenu(UIElement):
    def __init__(self, player: PlayerInfo, bounds: Rect, font: Font):
        super().__init__(bounds, None)
        self.money_count = Label(Rect(0, 0, 500, 500), Color('yellow'), font, '-')
        self.append_child(self.money_count)
        self.wood_count = Label(Rect(105, 0, 500, 500), Color('brown'), font, '-')
        self.append_child(self.wood_count)
        self.meat_count = Label(Rect(220, 0, 500, 500), Color('red'), font, '-/-')
        self.append_child(self.meat_count)
        self.player = player

    def update(self, event: pygame.event) -> bool:
        if super().update(event):
            return True
        self.update_values()
        return False

    def update_values(self) -> None:
        self.money_count.set_text(f'{self.player.resources.money}')
        self.wood_count.set_text(f'{self.player.resources.wood}')
        self.meat_count.set_text(f'{self.player.resources.meat}/{self.player.resources.max_meat}')
