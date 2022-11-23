import math
from functools import partial
from typing import Optional

import pygame
from pygame import Color

from src.client.action_sender import ClientActionSender
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.unit_production import UnitProductionComponent
from src.config import config
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, RequiredCost, EntityId
from src.elements.resources_display import ResourceDisplayMenu
from src.entities import entity_icons, entity_labels
from src.ui import UIElement, BorderParams, UIAnchor
from src.ui.button import UIButton
from src.ui.image import UIImage
from src.ui.text_label import TextLabel
from src.ui.types import PositionType, SizeType


class _QueueIcon(UIElement):
    def __init__(self, *,
                 current_unit_amount: int,
                 countdown_delay: int,

                 position: PositionType = (0, 0),
                 size: SizeType = (5, 5),
                 anchor: UIAnchor = UIAnchor.TOP_LEFT,

                 border_params: Optional[BorderParams] = None,
                 ):
        super().__init__(
            position=position,
            size=size,
            anchor=anchor,
            background_color=Color('lightblue'),
            border_params=border_params,
        )
        self.unit_amount = current_unit_amount
        self.frames = 0
        self.base_size = size
        self.countdown_delay = countdown_delay

        self.count_label = TextLabel(text=str(self.unit_amount), position=position, anchor=anchor)
        self.append_child(self.count_label)

    def add_unit(self):
        self.unit_amount += 1
        self.count_label.set_text(str(self.unit_amount))
        self.count_label.set_position(self._position)

    def pop_unit(self):
        self.unit_amount -= 1
        self.count_label.set_text(str(self.unit_amount))
        self.count_label.set_position(self._position)

    def on_update(self):
        additional_size = -math.cos(math.pi * self.frames / self.countdown_delay)
        self.set_size((self.base_size[0] + int(6 * additional_size), self.base_size[1] + int(6 * additional_size)))
        if not self.unit_amount:
            return

        self.frames += 1
        if self.frames >= self.countdown_delay:
            self.pop_unit()
            self.frames = 0


class ProduceMenu(UIElement):
    def __init__(self, ecs: EntityComponentSystem, action_sender: ClientActionSender, camera: Camera,
                 current_player: PlayerInfo, resource_menu: ResourceDisplayMenu):
        super().__init__()
        self._ecs = ecs
        self._selected_unit: EntityId | None = None
        self._action_sender = action_sender
        self._camera = camera
        self._current_player = current_player
        self._resource_menu = resource_menu

    def set_selected(self, build_entity_id: EntityId):
        self.children.clear()

        produce_component = self._ecs.get_component(build_entity_id, UnitProductionComponent)
        if produce_component is None:
            print('unit can not produce')
            return

        bottom_bar = UIElement(position=(config.minimap.bounds[3] + config.minimap.bounds[1],
                                         config.screen.size[1]),
                               size=(330, 60 * len(produce_component.producible_units) + 80),
                               anchor=UIAnchor.BOTTOM_LEFT,
                               background_color=Color(184, 187, 194), border_params=BorderParams(
                top_left_radius=15,
                top_right_radius=15,
            ))
        bottom_bar.append_child(
            TextLabel(text=f'Создание юнитов  Задержка: {produce_component.delay / 60:.0f}с', text_color=Color('black'),
                      position=bottom_bar._bounds.move(5, 5).topleft))
        queue_label = TextLabel(text=f'В очереди: ', text_color=Color('black'),
                      position=bottom_bar._bounds.move(5, 35).topleft)
        bottom_bar.append_child(queue_label)
        queue_icon = _QueueIcon(countdown_delay=produce_component.delay,
                                current_unit_amount=len(produce_component.unit_queue),
                                position=queue_label._bounds.move(15, 0).midright,
                                size=(35, 35),
                                anchor=UIAnchor.CENTER,

                                border_params=BorderParams(
                                   width=2,

                                   bottom_left_radius=5,
                                   bottom_right_radius=5,
                                   top_left_radius=5,
                                   top_right_radius=5,
                               ))
        bottom_bar.append_child(queue_icon)
        self.append_child(bottom_bar)

        for i, (unit_name, unit_cost) in enumerate(produce_component.producible_units.items()):
            icon_path = entity_icons[unit_name].format(color_name=self._current_player.color_name)

            btn = UIButton(position=(bottom_bar._bounds.x + 15, config.screen.rect.bottom - 15 - 60 * i),
                           size=(300, 50),
                           anchor=UIAnchor.BOTTOM_LEFT,

                           background_color=Color('lightgray'),
                           hover_color=Color('gray'),

                           border_params=BorderParams(
                               width=2,

                               bottom_left_radius=5,
                               bottom_right_radius=5,
                               top_left_radius=5,
                               top_right_radius=5,
                           ),
                           on_click=partial(self.produce_unit, unit_name, unit_cost, queue_icon),
                           on_mouse_hover=partial(self._resource_menu.display_cost, unit_cost),
                           on_mouse_exit=partial(self._resource_menu.hide_cost, unit_cost))
            icon = UIImage(image=icon_path,
                           position=btn._bounds.move(5, 0).midleft,
                           anchor=UIAnchor.MIDDLE_LEFT,
                           size=(40, 40))
            btn.append_child(icon)
            btn.append_child(TextLabel(text=entity_labels[unit_name],
                                       position=icon._bounds.move(15, 0).midright,
                                       anchor=UIAnchor.MIDDLE_LEFT))

            bottom_bar.append_child(btn)

        self._selected_unit = build_entity_id

    def unselect(self):
        self.children.clear()
        self._selected_unit = None

    def produce_unit(self, unit_name: str, unit_cost: RequiredCost, queue_icon: _QueueIcon) -> bool:
        if not self._current_player.has_enough(unit_cost):
            self._current_player.play_not_enough_sound(unit_cost)
            return False

        self._action_sender.produce_unit(self._selected_unit, unit_name)
        queue_icon.add_unit()

    def draw(self, screen) -> None:
        super().draw(screen)

        if self._selected_unit is not None:
            position, texture = self._ecs.get_components(self._selected_unit, (PositionComponent, TextureComponent))
            rect = texture.texture.get_rect()
            rect.center = position.x + self._camera.offset_x, position.y + self._camera.offset_y
            pygame.draw.rect(screen, self._current_player.color, rect, 1, 15)

    def on_death(self, entity_id: EntityId):
        if self._selected_unit == entity_id:
            self.unselect()

    def update(self, event) -> bool:
        if super().update(event):
            return True

        if event.type == pygame.MOUSEBUTTONUP and self.on_mouse_click(event.button):
            return True

        return False

    def on_mouse_click(self, button: int) -> bool | None:
        if button != pygame.BUTTON_LEFT:
            self.unselect()
            return

        mouse_pos = self._camera.get_in_game_mouse_position()

        for entity_id, components in self._ecs.get_entities_with_components((UnitProductionComponent,
                                                                             PositionComponent,
                                                                             TextureComponent,
                                                                             PlayerOwnerComponent)):
            unit_production, position, texture, owner = components

            if owner.socket_id != self._current_player.socket_id:
                continue

            rect: pygame.Rect = texture.texture.get_rect()
            rect.center = position.to_tuple()

            if rect.collidepoint(*mouse_pos):
                self.set_selected(entity_id)
                return True

        self.unselect()
