import pygame.event
from pygame import Rect, Color

from src.client.action_sender import ClientActionSender
from src.components.chase import ChaseComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import EntityId, PlayerInfo
from src.ui import UIElement
from src.utils.math_utils import rect_by_two_points, spread_position


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

            pygame.draw.rect(screen, Color('blue'), render_rect, 2)

        if self.selected_entities:
            for entity_id in self.selected_entities:
                position, texture = self.ecs.get_components(entity_id, (PositionComponent, TextureComponent))
                rect = texture.texture.get_rect()
                rect.center = self.camera.to_screen_position(position.to_tuple())
                pygame.draw.ellipse(screen, Color('blue'), rect, 1)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_click_position = self.camera.get_in_game_mouse_position()

        elif event.type == pygame.MOUSEBUTTONUP:

            if self.selected_entities:
                mouse_up_position = self.camera.get_in_game_mouse_position()
                for entity_id in self.selected_entities:
                    chase = self.ecs.get_component(entity_id, ChaseComponent)
                    chase.chase_position = PositionComponent(*spread_position(mouse_up_position, 100))

                self.mouse_click_position = None
                self.selected_entities.clear()

                return True

            if self.mouse_click_position is not None:
                if self.mouse_click_position == self.camera.get_in_game_mouse_position():
                    self.mouse_click_position = None
                    return False

                mouse_up_position = self.camera.get_in_game_mouse_position()
                self.selected_entities.clear()
                selection_rect = rect_by_two_points(mouse_up_position, self.mouse_click_position)

                for entity_id, (position, chase, player) in self.ecs.get_entities_with_components(
                        (PositionComponent, ChaseComponent, PlayerOwnerComponent)):

                    if not selection_rect.collidepoint(*position.to_tuple()):
                        continue

                    if self.current_player.socket_id != player.socket_id:
                        continue

                    self.selected_entities.add(entity_id)

                print(self.selected_entities)

                self.mouse_click_position = None
                return True
