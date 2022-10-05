import pygame.event
from pygame import Rect

from src.client.action_sender import ClientActionSender
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.chase import ChaseComponent
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId, PlayerInfo
from src.ui import UIElement
from src.utils.math_utils import rect_by_two_points


class UnitMoveMenu(UIElement):
    def __init__(self, ecs: EntityComponentSystem, action_sender: ClientActionSender, camera: Camera, current_player: PlayerInfo):
        super().__init__(Rect(0, 0, 0, 0), None)
        self.ecs = ecs
        self.action_sender = action_sender
        self.camera = camera
        self.current_player = current_player

        self.mouse_click_position: tuple[float, float] | None = None
        self.selected_entities: set[EntityId] = set()

    def draw(self, screen):
        if self.mouse_click_position is not None:
            pos = self.camera.to_screen_position(self.mouse_click_position)
            mouse_pos = pygame.mouse.get_pos()

            render_rect = rect_by_two_points(pos, mouse_pos)

            if not(render_rect.width <= 40 and render_rect.height <= 40):
                pygame.draw.rect(screen, self.current_player.color, render_rect, 2)

        if self.selected_entities:
            for entity_id in self.selected_entities:
                components = self.ecs.get_components(entity_id, (PositionComponent, TextureComponent))

                position, texture = components
                rect = texture.texture.get_rect()
                rect.center = self.camera.to_screen_position(position.to_tuple())
                pygame.draw.ellipse(screen, self.current_player.color, rect, 1)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.selected_entities:
                self.mouse_click_position = self.camera.get_in_game_mouse_position()

        elif event.type == pygame.MOUSEBUTTONUP:

            if self.selected_entities:
                mouse_up_position = self.camera.get_in_game_mouse_position()

                self.action_sender.force_to_move(self.selected_entities, mouse_up_position)

                self.mouse_click_position = None
                self.selected_entities.clear()
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                return True

            if self.mouse_click_position is not None:

                mouse_up_position = self.camera.get_in_game_mouse_position()
                self.selected_entities.clear()
                selection_rect = rect_by_two_points(mouse_up_position, self.mouse_click_position)

                if selection_rect.width <= 40 and selection_rect.height <= 40:
                    self.mouse_click_position = None
                    return False

                for entity_id, (position, chase, player) in self.ecs.get_entities_with_components(
                        (PositionComponent, ChaseComponent, PlayerOwnerComponent)):

                    if not selection_rect.collidepoint(*position.to_tuple()):
                        continue

                    if self.current_player.socket_id != player.socket_id:
                        continue

                    self.selected_entities.add(entity_id)

                if self.selected_entities:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                self.mouse_click_position = None
                return True
