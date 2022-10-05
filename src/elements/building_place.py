from typing import NamedTuple

import pygame
from pydantic.main import partial
from pygame.rect import Rect
from pygame.surface import Surface

from src.client.action_sender import ClientActionSender
from src.core.camera import Camera
from src.core.types import RequiredCost, PlayerInfo
from src.entities import buildings, entity_icons
from src.elements.resources_display import ResourceDisplayMenu
from src.ui import UIElement, UIButton, UIImage
from src.utils.image import get_image


class SelectedBuilding(NamedTuple):
    build_name: str
    cost: RequiredCost
    image: Surface


class BuildMenu(UIElement):
    def __init__(self, bounds, resource_menu: ResourceDisplayMenu, action_sender: ClientActionSender,
                 current_player: PlayerInfo, camera: Camera):
        super().__init__(bounds, None)
        self.camera = camera
        self.current_player = current_player
        self.selected: SelectedBuilding | None = None
        self.resource_menu = resource_menu
        self.action_sender = action_sender
        for i, (build_name, cost) in enumerate(buildings.items()):
            image = get_image(entity_icons[build_name].format(color_name=self.current_player.color_name))
            btn = UIButton(Rect(0, i * 55 + 15, 50, 50), None, partial(self.select_building, build_name, cost, image))
            btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, image))
            self.append_child(btn)

    def draw(self, screen) -> None:
        if self.selected:
            r = self.selected.image.get_rect()
            r.center = pygame.mouse.get_pos()
            screen.blit(self.selected.image, r)
        super().draw(screen)

    def update(self, event) -> bool:
        if super().update(event):
            return True

        if self.selected:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.place_building(self.camera.get_in_game_mouse_position())
                    return True
                if event.button == 3:
                    self.unselect_building()
                    return True
        return False

    def select_building(self, build_name: str, cost: RequiredCost, image: Surface):
        self.selected = SelectedBuilding(build_name, cost, image)
        self.resource_menu.display_cost(cost)

    def unselect_building(self):
        self.resource_menu.hide_cost(self.selected.cost)
        self.selected = None

    def place_building(self, position: tuple[float, float]):
        if not self.current_player.has_enough(self.selected.cost):
            print('Not enough money')
            return

        self.action_sender.place_building(self.selected.build_name, position)
