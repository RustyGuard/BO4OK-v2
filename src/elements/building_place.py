from functools import partial
from typing import NamedTuple, Optional

import pygame
from pygame import Color
from pygame.surface import Surface

from src.client.action_sender import ClientActionSender
from src.constants import SoundCode
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import RequiredCost, PlayerInfo
from src.elements.resources_display import ResourceDisplayMenu
from src.entities import buildings, entity_icons, entity_labels
from src.sound_player import play_sound
from src.ui import UIElement, TextLabel, UIAnchor, BorderParams
from src.ui.button import UIButton
from src.ui.image import UIImage
from src.ui.types import PositionType, SizeType
from src.utils.collision import can_be_placed
from src.utils.image import get_image


class SelectedBuilding(NamedTuple):
    build_name: str
    cost: RequiredCost
    image: Surface


class BuildMenu(UIElement):
    def __init__(self, resource_menu: ResourceDisplayMenu, action_sender: ClientActionSender,
                 current_player: PlayerInfo, camera: Camera, ecs: EntityComponentSystem):
        super().__init__()
        self.camera = camera
        self.current_player = current_player
        self.selected: SelectedBuilding | None = None
        self.resource_menu = resource_menu
        self.action_sender = action_sender
        self.ecs = ecs
        for i, (build_name, cost) in enumerate(buildings.items()):
            image = get_image(entity_icons[build_name].format(color_name=self.current_player.color_name))
            btn = UIButton(position=(5, i * 55 + 15),
                           size=(200, 50),
                           background_color=Color('lightgray'),
                           hover_color=Color('gray'),

                           border_params=BorderParams(
                               width=2,

                               bottom_left_radius=5,
                               bottom_right_radius=5,
                               top_left_radius=5,
                               top_right_radius=5,
                           ),

                           on_click=partial(self.select_building, build_name, cost, image))
            btn.append_child(UIImage(image=image,
                                     position=btn._bounds.move(5, 0).midleft,
                                     size=(40, 40),
                                     anchor=UIAnchor.MIDDLE_LEFT))
            self.append_child(btn)

            label = TextLabel(text=entity_labels[build_name],
                              position=btn._bounds.move(-15, 0).midright,
                              anchor=UIAnchor.MIDDLE_RIGHT,
                              )
            self.append_child(label)

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
            self.current_player.play_not_enough_sound(self.selected.cost)
            print('Not enough money')
            return

        building_texture_path = entity_icons[self.selected.build_name].format(color_name=self.current_player.color_name)
        building_texture = get_image(building_texture_path)

        if not can_be_placed(self.ecs, position, building_texture.get_rect().size):
            print('Can not build on top of entity')
            play_sound(SoundCode.PLACE_OCCUPIED)
            return

        self.action_sender.place_building(self.selected.build_name, position)
