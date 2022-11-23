from functools import partial
from typing import NamedTuple

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
from src.utils.collision import can_be_placed
from src.utils.image import get_image


class _SelectedBuilding(NamedTuple):
    build_name: str
    cost: RequiredCost
    image: Surface


class BuildMenu(UIElement):
    def __init__(self, resource_menu: ResourceDisplayMenu, action_sender: ClientActionSender,
                 current_player: PlayerInfo, camera: Camera, ecs: EntityComponentSystem):
        super().__init__()
        self._camera = camera
        self._current_player = current_player
        self._selected: _SelectedBuilding | None = None
        self._resource_menu = resource_menu
        self._action_sender = action_sender
        self._ecs = ecs
        for i, (build_name, cost) in enumerate(buildings.items()):
            image = get_image(entity_icons[build_name].format(color_name=self._current_player.color_name))
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
        if self._selected:
            r = self._selected.image.get_rect()
            r.center = pygame.mouse.get_pos()
            screen.blit(self._selected.image, r)
        super().draw(screen)

    def on_mouse_button_up(self, mouse_position: tuple[int, int], button: int) -> bool | None:
        if not self._selected:
            return

        if button == pygame.BUTTON_LEFT:
            self.place_building(self._camera.get_in_game_mouse_position())
            return True

        if button == pygame.BUTTON_RIGHT:
            self.unselect_building()
            return True

    def select_building(self, build_name: str, cost: RequiredCost, image: Surface):
        self._selected = _SelectedBuilding(build_name, cost, image)
        self._resource_menu.display_cost(cost)

    def unselect_building(self):
        self._resource_menu.hide_cost(self._selected.cost)
        self._selected = None

    def place_building(self, position: tuple[float, float]):
        if not self._current_player.has_enough(self._selected.cost):
            self._current_player.play_not_enough_sound(self._selected.cost)
            print('Not enough money')
            return

        building_texture_path = entity_icons[self._selected.build_name].format(color_name=self._current_player.color_name)
        building_texture = get_image(building_texture_path)

        if not can_be_placed(self._ecs, position, building_texture.get_rect().size):
            print('Can not build on top of entity')
            play_sound(SoundCode.PLACE_OCCUPIED)
            return

        self._action_sender.place_building(self._selected.build_name, position)
