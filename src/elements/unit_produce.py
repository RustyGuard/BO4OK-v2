from functools import partial

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
from src.entities import entity_icons
from src.ui import UIElement, BorderParams, UIAnchor
from src.ui.button import UIButton
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class ProduceMenu(UIElement):
    def __init__(self, ecs: EntityComponentSystem, action_sender: ClientActionSender, camera: Camera,
                 current_player: PlayerInfo, resource_menu: ResourceDisplayMenu):
        super().__init__()
        self.ecs = ecs
        self.selected_unit: EntityId | None = None
        self.action_sender = action_sender
        self.camera = camera
        self.current_player = current_player
        self.resource_menu = resource_menu

    def set_selected(self, build_entity_id: EntityId):
        self.children.clear()

        produce_component = self.ecs.get_component(build_entity_id, UnitProductionComponent)
        if produce_component is None:
            print('unit can not produce')
            return

        bottom_bar = UIElement(position=(config.minimap.bounds[3] + config.minimap.bounds[1],
                                         config.screen.size[1]), size=(450, 120), anchor=UIAnchor.BOTTOM_LEFT,
                               background_color=Color(184, 187, 194), border_params=BorderParams(
                top_left_radius=15,
                top_right_radius=15,
            ))
        bottom_bar.append_child(TextLabel(text='Создание юнитов', text_color=Color('black'),
                                          position=bottom_bar._bounds.move(5, 5).topleft))
        self.append_child(bottom_bar)

        for i, (unit_name, unit_cost) in enumerate(produce_component.producible_units.items()):
            icon_path = entity_icons[unit_name].format(color_name=self.current_player.color_name)

            btn = UIButton(position=(bottom_bar._bounds.x + 5 + 85 * i, bottom_bar._bounds.y + 35), size=(80, 80),
                           on_click=partial(self.produce_unit, unit_name, unit_cost),
                           on_mouse_hover=partial(self.resource_menu.display_cost, unit_cost),
                           on_mouse_exit=partial(self.resource_menu.hide_cost, unit_cost))
            btn.append_child(UIImage(image=icon_path, position=btn._bounds.topleft, size=btn._bounds.size))

            bottom_bar.append_child(btn)

        self.selected_unit = build_entity_id

    def unselect(self):
        self.children.clear()
        self.selected_unit = None

    def produce_unit(self, unit_name: str, unit_cost: RequiredCost) -> None:
        if not self.current_player.has_enough(unit_cost):
            self.current_player.play_not_enough_sound(unit_cost)
            return

        self.action_sender.produce_unit(self.selected_unit, unit_name)

    def draw(self, screen) -> None:
        super().draw(screen)

        if self.selected_unit is not None:
            position, texture = self.ecs.get_components(self.selected_unit, (PositionComponent, TextureComponent))
            rect = texture.texture.get_rect()
            rect.center = position.x + self.camera.offset_x, position.y + self.camera.offset_y
            pygame.draw.rect(screen, self.current_player.color, rect, 1, 15)

    def on_death(self, entity_id: EntityId):
        if self.selected_unit == entity_id:
            self.unselect()

    def update(self, event) -> bool:
        if super().update(event):
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = self.camera.get_in_game_mouse_position()

            for entity_id, components in self.ecs.get_entities_with_components((UnitProductionComponent,
                                                                                PositionComponent,
                                                                                TextureComponent,
                                                                                PlayerOwnerComponent)):
                unit_production, position, texture, owner = components

                if owner.socket_id != self.current_player.socket_id:
                    continue

                rect: pygame.Rect = texture.texture.get_rect()
                rect.center = position.to_tuple()

                if rect.collidepoint(*mouse_pos):
                    self.set_selected(entity_id)
                    return True

            self.unselect()

        return False
