from pygame import Rect
from pygame.font import Font

from src.client.action_sender import ClientActionSender
from src.config import config
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo
from src.elements.building_place import BuildMenu
from src.elements.camera_input import CameraInputHandler
from src.elements.damage_indicators import DamageIndicators
from src.elements.game_end.defeat_screen import DefeatScreen
from src.elements.game_end.victory_screen import VictoryScreen
from src.elements.minimap import Minimap
from src.elements.pause_menu import PauseMenu
from src.elements.renderers.entities_renderer import EntitiesRenderer
from src.elements.renderers.grass_background import GrassBackground
from src.elements.resources_display import ResourceDisplayMenu
from src.elements.unit_move import UnitMoveMenu
from src.elements.unit_produce import ProduceMenu
from src.ui import UIElement, UIImage, UIAnchor


class GameComposer(UIElement):
    def __init__(self, ecs: EntityComponentSystem, current_player: PlayerInfo, action_sender: ClientActionSender):
        super().__init__()

        self.ecs = ecs
        self.current_layer = current_player
        self.action_sender = action_sender

        self.camera = Camera()

        self.damage_indicators = DamageIndicators(self.camera)

        self.append_child(GrassBackground(self.camera))
        self.append_child(EntitiesRenderer(self.ecs, self.camera))
        self.append_child(self.damage_indicators)

        self.minimap = Minimap(self.ecs, self.camera, self.current_layer.color)
        self.minimap_elem = UIImage(image='assets/ui/minimap.png',
                                    position=(0, config.screen.height),
                                    anchor=UIAnchor.BOTTOM_LEFT)
        self.minimap_elem.append_child(self.minimap)
        self.resource_menu = ResourceDisplayMenu(self.current_layer,
                                                 Rect(self.minimap._bounds.move(0, -33).topleft, (0, 0)),
                                                 Font('assets/fonts/arial.ttf', 25),
                                                 Font('assets/fonts/arial.ttf', 20))

        self.build_menu = BuildMenu(self.resource_menu, self.action_sender, self.current_layer, self.camera,
                                    self.ecs)
        self.append_child(self.build_menu)

        self.produce_menu = ProduceMenu(self.ecs, self.action_sender, self.camera, self.current_layer,
                                        self.resource_menu)
        self.append_child(self.produce_menu)

        self.unit_move_menu = UnitMoveMenu(
            self.ecs,
            self.action_sender,
            self.camera,
            self.current_layer,
        )

        self.minimap_elem.append_child(self.resource_menu)
        self.append_child(self.unit_move_menu)
        self.append_child(self.minimap_elem)

        self.append_child(CameraInputHandler(self.camera))
        self.append_child(PauseMenu())

    def disable_player_actions(self):
        self.children.remove(self.build_menu)
        self.children.remove(self.produce_menu)
        self.children.remove(self.unit_move_menu)

    def on_update(self):
        self.ecs.update()

    def show_defeat_screen(self):
        self.disable_player_actions()

        defeat_screen = DefeatScreen()
        self.append_child(defeat_screen)
        defeat_screen.show_screen()

    def show_victory_screen(self):
        victory_screen = VictoryScreen()
        self.append_child(victory_screen)
        victory_screen.show_screen()
