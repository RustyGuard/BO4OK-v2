import math
import random

import pygame
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect
from setuptools._distutils.command.config import config

from src.client.action_sender import ClientActionSender
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.config import config
from src.constants import EVENT_SEC
from src.core.camera import Camera
from src.core.types import PlayerInfo, RequiredCost
# from src.entities.units_base import ProducingBuilding
from src.entities import entity_icons
from src.entity_component_system import EntityComponentSystem, EntityId
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
        def __init__(self, name: str, icon_path: str, cost: RequiredCost, bounds: Rect):
            self.name = name
            self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            self.icon = pygame.image.load(icon_path)
            self.cost = cost
            self.bounds = bounds

    def __init__(self, bounds, ecs: EntityComponentSystem, action_sender: ClientActionSender, camera: Camera,
                 current_player: PlayerInfo, resource_menu: 'ResourceMenu'):
        super().__init__(bounds, None)
        self.ecs = ecs
        self.units = {}
        self.selected_unit: EntityId | None = None
        self.action_sender = action_sender
        self.camera = camera
        self.current_player = current_player
        self.resource_menu = resource_menu

    def set_selected(self, build_entity_id: EntityId):
        self.childs.clear()

        produce_component = self.ecs.get_component(build_entity_id, UnitProductionComponent)
        if produce_component is None:
            print('unit can not produce')
            return

        bottom_bar = UIElement(Rect(config['minimap']['bounds'][3] + config['minimap']['bounds'][1],
                                    config['screen']['size'][1] - 120,
                                    450,
                                    120), Color(184, 187, 194), border_top_left_radius=15,
                               border_top_right_radius=15)
        bottom_bar.append_child(Label(Rect(5, 5, 450, 60), Color('black'), Font('assets/fonts/arial.ttf', 20), 'Создание юнитов'))
        self.append_child(bottom_bar)
        for i, (unit_name, unit_cost) in enumerate(produce_component.producible_units.items()):
            unit_cost = RequiredCost(**unit_cost)
            icon_path = entity_icons[unit_name]

            btn = UIButton(Rect(5 + 80 * i, 35, 80, 80), None, self.select, unit_name)
            btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, pygame.image.load(icon_path)))

            bottom_bar.append_child(btn)
            self.units[unit_name] = self.ProduceMenuItem(unit_name, icon_path, unit_cost, btn.absolute_bounds)

        self.selected_unit = build_entity_id

    def select(self, unit_name: str) -> None:
        self.action_sender.produce_unit(self.selected_unit, unit_name)

    def draw(self, screen) -> None:
        super().draw(screen)

        if self.selected_unit:
            position, texture = self.ecs.get_components(self.selected_unit, [PositionComponent, TextureComponent])
            rect = texture.texture.get_rect()
            rect.center = position.x + self.camera.offset_x, position.y + self.camera.offset_y
            pygame.draw.rect(screen, Color(255, 255, 255, 0), rect, 1, 15)

    def update(self, event) -> bool:
        if super().update(event):
            return True

        if event.type == pygame.MOUSEMOTION:
            for item in self.units.values():
                mouse_pos = pygame.mouse.get_pos()
                if item.bounds.collidepoint(*mouse_pos):
                    print(item.cost)
                    self.resource_menu.display_cost(item.cost)
                    break
            else:
                self.resource_menu.display_cost(None)

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = self.camera.get_in_game_mouse_position()

            for entity_id, components in self.ecs.get_entities_with_components([UnitProductionComponent,
                                                                                PositionComponent,
                                                                                TextureComponent,
                                                                                PlayerOwnerComponent]):
                unit_production, position, texture, owner = components
                if owner.socket_id != self.current_player.socket_id:
                    continue

                rect: pygame.Rect = texture.texture.get_rect()
                rect.center = position.to_tuple()

                if rect.collidepoint(*mouse_pos):
                    self.set_selected(entity_id)
                    break

        return False


class ResourceMenu(UIElement):
    def __init__(self, player: PlayerInfo, bounds: Rect, font: Font):
        super().__init__(bounds, None)
        self.money_count = Label(Rect(0, 0, 500, 500), Color('yellow'), font, '-')
        self.append_child(self.money_count)
        self.wood_count = Label(Rect(105, 0, 500, 500), Color('brown'), font, '-')
        self.append_child(self.wood_count)
        self.meat_count = Label(Rect(220, 0, 500, 500), Color('pink'), font, '-/-')
        self.append_child(self.meat_count)
        self.player = player
        self.cost: RequiredCost | None = None

    def display_cost(self, cost: RequiredCost):
        self.cost = cost

    def update(self, event: pygame.event) -> bool:
        if super().update(event):
            return True
        self.update_values()
        return False

    def update_values(self) -> None:
        if self.cost:

            self.money_count.set_text(f'{self.player.resources.money - self.cost.money}')
            if self.cost.money:
                self.money_count.set_color(Color('red'))
            self.wood_count.set_text(f'{self.player.resources.wood - self.cost.wood}')
            if self.cost.wood:
                self.wood_count.set_color(Color('red'))
            self.meat_count.set_text(f'{self.player.resources.meat + self.cost.meat}/{self.player.resources.max_meat}')
            if self.cost.meat:
                self.meat_count.set_color(Color('red'))
        else:

            self.money_count.set_text(f'{self.player.resources.money}')
            self.money_count.set_color(Color('yellow'))
            self.wood_count.set_text(f'{self.player.resources.wood}')
            self.wood_count.set_color(Color('brown'))
            self.meat_count.set_text(f'{self.player.resources.meat}/{self.player.resources.max_meat}')
            self.meat_count.set_color(Color('pink'))
