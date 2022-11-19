import socket
from multiprocessing import Process
from multiprocessing.connection import Connection
from typing import Any

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from src.client.action_sender import ClientActionSender
from src.components.base.collider import ColliderComponent
from src.components.base.decay import DecayComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.base.velocity import VelocityComponent
from src.components.chase import ChaseComponent
from src.components.core_building import CoreBuildingComponent
from src.components.fighting.close_range_attack import CloseRangeAttackComponent
from src.components.fighting.damage_on_contact import DamageOnContactComponent
from src.components.fighting.enemy_finder import EnemyFinderComponent
from src.components.fighting.health import HealthComponent
from src.components.fighting.projectile_throw import ProjectileThrowComponent
from src.components.meat import ReturnMeatOnDeathComponent, MaxMeatIncreaseComponent
from src.components.minimap_icon import MinimapIconComponent
from src.components.unit_production import UnitProductionComponent
from src.components.worker.depot import ResourceDepotComponent
from src.components.worker.resource import ResourceComponent
from src.components.worker.resource_gatherer import ResourceGathererComponent
from src.components.worker.uncompleted_building import UncompletedBuildingComponent
from src.components.worker.work_finder import WorkFinderComponent
from src.config import config
from src.constants import HOST_PLAYER_ID
from src.core.camera import Camera
from src.core.entity_component_system import EntityComponentSystem
from src.core.types import PlayerInfo, Component, EntityId, PlayerState
from src.elements.building_place import BuildMenu
from src.elements.camera_input import CameraInputHandler
from src.elements.game_end.defeat_screen import DefeatScreen
from src.elements.game_end.victory_screen import VictoryScreen
from src.elements.minimap import Minimap
from src.elements.pause_menu import PauseMenu
from src.elements.renderers.entities_renderer import EntitiesRenderer
from src.elements.renderers.grass_background import GrassBackground
from src.elements.resources_display import ResourceDisplayMenu
from src.elements.unit_move import UnitMoveMenu
from src.elements.unit_produce import ProduceMenu
from src.server.action_handler import ServerActionHandler
from src.server.action_sender import ServerActionSender
from src.server.level_setup import setup_level
from src.server.socket_threads import Connections
from src.sound_player import play_music
from src.systems.base.colliders import collider_system
from src.systems.base.death import death_system
from src.systems.base.decay import decay_system
from src.systems.base.velocity import velocity_system
from src.systems.chase import chase_system
from src.systems.fighting.close_range_attack import close_range_attack_system
from src.systems.fighting.damage_on_contact import damage_on_contact_system
from src.systems.fighting.enemy_finder import enemy_finder_system
from src.systems.fighting.projectile_throw import projectile_throw_system
from src.systems.max_meat_increase import max_meat_increase_system
from src.systems.unit_production import unit_production_system
from src.systems.worker.building_completion import building_completion_system
from src.systems.worker.resource_gathering import working_system
from src.systems.worker.work_finder import work_finder_system
from src.ui import UIElement
from src.ui.fps_counter import FPSCounter
from src.ui.image import UIImage


class ServerGameMenu(UIElement):
    def __init__(self, server_socket: socket.socket, connections: Connections, received_actions: list[tuple[int, Any]],
                 write_action_connection: Connection, send_process: Process, players: dict[int, PlayerInfo]):
        super().__init__(config.screen.rect, Color(93, 161, 48))

        self.players = players

        fps_font = Font('assets/fonts/arial.ttf', 20)

        sub_elem = UIElement(Rect(50, 50, 50, 50), None)
        sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
        self.append_child(sub_elem)

        self.socket = server_socket
        self.connections = connections
        self.received_actions = received_actions
        self.write_action_connection = write_action_connection
        self.send_process = send_process

        self.camera = Camera()

        self.action_sender = ServerActionSender(self.write_action_connection, self.camera)

        self.local_action_sender = ClientActionSender(self.write_local_action)
        self.local_player = players[-1]

        self.ecs = EntityComponentSystem(self.on_create, self.on_remove)

        self.ecs.add_variable('action_sender', self.action_sender)
        self.ecs.add_variable('players', self.players)

        self.ecs.init_component(PositionComponent)
        self.ecs.init_component(VelocityComponent)
        self.ecs.init_component(DecayComponent)
        self.ecs.init_component(TextureComponent)
        self.ecs.init_component(MinimapIconComponent)
        self.ecs.init_component(UnitProductionComponent)
        self.ecs.init_component(PlayerOwnerComponent)
        self.ecs.init_component(ChaseComponent)
        self.ecs.init_component(EnemyFinderComponent)
        self.ecs.init_component(HealthComponent)
        self.ecs.init_component(ProjectileThrowComponent)
        self.ecs.init_component(DamageOnContactComponent)
        self.ecs.init_component(CloseRangeAttackComponent)
        self.ecs.init_component(ReturnMeatOnDeathComponent)
        self.ecs.init_component(MaxMeatIncreaseComponent)
        self.ecs.init_component(WorkFinderComponent)
        self.ecs.init_component(ResourceComponent)
        self.ecs.init_component(ResourceDepotComponent)
        self.ecs.init_component(ResourceGathererComponent)
        self.ecs.init_component(UncompletedBuildingComponent)
        self.ecs.init_component(ColliderComponent)
        self.ecs.init_component(CoreBuildingComponent)

        self.ecs.init_system(velocity_system)
        self.ecs.init_system(decay_system)
        self.ecs.init_system(unit_production_system)
        self.ecs.init_system(chase_system)
        self.ecs.init_system(enemy_finder_system)
        self.ecs.init_system(projectile_throw_system)
        self.ecs.init_system(damage_on_contact_system)
        self.ecs.init_system(close_range_attack_system)
        self.ecs.init_system(death_system)
        self.ecs.init_system(max_meat_increase_system)
        self.ecs.init_system(work_finder_system)
        self.ecs.init_system(working_system)
        self.ecs.init_system(building_completion_system)
        self.ecs.init_system(collider_system)

        self.action_handler = ServerActionHandler(self.ecs, self.players, self.action_sender)

        self.append_child(GrassBackground(self.camera))
        self.append_child(EntitiesRenderer(self.ecs, self.camera))

        self.minimap = Minimap(self.ecs, self.camera, self.local_player.color)
        self.minimap_elem = UIImage(Rect(0, config.screen.size[1] - 388, 0, 0), 'assets/ui/minimap.png')
        self.minimap_elem.append_child(self.minimap)
        self.resource_menu = ResourceDisplayMenu(self.local_player,
                                                 Rect(self.minimap.bounds.move(0, -33).topleft, (0, 0)),
                                                 Font('assets/fonts/arial.ttf', 25))

        self.build_menu = BuildMenu(self.bounds, self.resource_menu, self.local_action_sender,
                                    self.local_player, self.camera, self.ecs)
        self.append_child(self.build_menu)

        self.produce_menu = ProduceMenu(self.bounds, self.ecs, self.local_action_sender, self.camera,
                                        self.local_player, self.resource_menu)
        self.append_child(self.produce_menu)

        self.unit_move_menu = UnitMoveMenu(
            self.ecs,
            self.local_action_sender,
            self.camera,
            self.local_player,
        )

        self.minimap_elem.append_child(self.resource_menu)
        self.append_child(self.unit_move_menu)
        self.append_child(self.minimap_elem)

        self.append_child(CameraInputHandler(self.camera))
        self.append_child(PauseMenu())

        setup_level(self.ecs, self.players)

        self.defeat_screen = DefeatScreen()
        self.append_child(self.defeat_screen)

        self.victory_screen = VictoryScreen()
        self.append_child(self.victory_screen)

        play_music('assets/music/game1.ogg')

    def write_local_action(self, action: list):
        self.received_actions.append((-1, action))

    def on_create(self, entity_id, components: list[Component]):
        components_to_exclude = (
            DecayComponent,
            EnemyFinderComponent,
            ProjectileThrowComponent,
            DamageOnContactComponent,
            CloseRangeAttackComponent,
            ReturnMeatOnDeathComponent,
            MaxMeatIncreaseComponent,
            WorkFinderComponent,
            ResourceGathererComponent,
            ResourceDepotComponent,
            CoreBuildingComponent,
        )
        components = [component for component in components if type(component) not in components_to_exclude]

        self.action_sender.send_entity(entity_id, components)

    def is_defeated(self, player_id: int, entity_to_ignore: EntityId):
        if self.players[player_id].current_state != PlayerState.BATTLER:
            return False

        for entity, (owner, _) in self.ecs.get_entities_with_components((PlayerOwnerComponent, CoreBuildingComponent)):
            if entity != entity_to_ignore and owner.socket_id == player_id:
                return False
        return True

    def is_winner(self, player_id: int, entity_to_ignore: EntityId):
        if self.players[player_id].current_state != PlayerState.BATTLER:
            return False

        for entity, (owner, _) in self.ecs.get_entities_with_components((PlayerOwnerComponent, CoreBuildingComponent)):
            if entity != entity_to_ignore and owner.socket_id != player_id:
                return False
        return True

    def mark_as_defeated(self, player_id: int):
        if self.players[player_id].current_state != PlayerState.BATTLER:
            return

        self.players[player_id].current_state = PlayerState.SPECTATOR

        if player_id == HOST_PLAYER_ID:
            self.defeat_screen.show_screen()
            return
        self.action_sender.show_defeat(player_id)

    def mark_as_winner(self, player_id: int):
        if self.players[player_id].current_state != PlayerState.BATTLER:
            return

        self.players[player_id].current_state = PlayerState.WINNER

        if player_id == HOST_PLAYER_ID:
            self.victory_screen.show_screen()
            return
        self.action_sender.show_victory(player_id)

    def check_for_game_over_on_death(self, entity_id: EntityId):
        components = self.ecs.get_components(entity_id, (PlayerOwnerComponent, CoreBuildingComponent))
        if components is None:
            return

        owner, _ = components

        if self.is_defeated(owner.socket_id, entity_id):
            self.mark_as_defeated(owner.socket_id)

        for player in self.players.values():
            if self.is_winner(player.socket_id, entity_id):
                self.mark_as_winner(player.socket_id)
                break

    def drop_chase_targets(self, entity_id: EntityId):
        for chase_entity_id, (chase,) in self.ecs.get_entities_with_components((ChaseComponent,)):
            if chase.entity_id == entity_id:
                chase.drop_target()

    def on_remove(self, entity_id: EntityId):
        self.produce_menu.on_death(entity_id)
        self.unit_move_menu.on_death(entity_id)

        self.drop_chase_targets(entity_id)
        self.check_for_game_over_on_death(entity_id)

        self.action_sender.remove_entity(entity_id)

    def on_update(self):
        while self.received_actions:
            sender, (command, *args) = self.received_actions.pop(0)
            self.action_handler.handle_action(command, args, sender)

        self.ecs.update()
        self.resource_menu.update_values()

    def shutdown(self) -> None:
        self.send_process.terminate()
        self.write_action_connection.close()
        self.socket.close()
