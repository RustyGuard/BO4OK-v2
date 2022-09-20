import json
import os
from enum import Enum, auto
from functools import wraps
from multiprocessing.connection import Connection
from typing import Tuple, Any, Optional, Type

import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.sprite import Group, Sprite

from src.config import config
from src.constants import EVENT_SEC
from src.core.camera import Camera
from src.core.types import PlayerInfo, RequiredCost
from src.entities.units_base import Fighter, Unit, TwistUnit, ProducingBuilding, Projectile
from src.utils import UniqueIdGenerator


def _side_only(side):
    def side_only_dec(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.side != side:
                raise Exception(f'No supported on {self.side}')
            return func(self, *args, **kwargs)

        return wrapper

    return side_only_dec


class Game:
    class Side(Enum):
        SERVER = auto()
        CLIENT = auto()

    class ClientCommands:
        """Команды, отправляемые клиенту"""
        CREATE = 1
        UPDATE = 2
        TARGET_CHANGE = 3
        RESOURCE_INFO = 4
        HEALTH_INFO = 5
        DEAD = 6

    class ServerCommands:
        """Команды, отправляемые серверу"""
        PLACE_UNIT = 1
        SET_TARGET_MOVE = 2
        PRODUCE_UNIT = 3

    def __init__(self, side: Side, mod_loader: 'ModLoader', send_connection: Connection,
                 players: list[PlayerInfo], current_team: int):
        self.mod_loader: ModLoader = mod_loader
        self.side = side
        self.sprites = Group()
        self.world_size = config['world']['size']
        self.world_rect = Rect(-self.world_size, -self.world_size, self.world_size * 2, self.world_size * 2)
        self.send_connection = send_connection
        self.camera = Camera(self)

        self.players = players
        self.current_team = current_team

        if self.side == Game.Side.SERVER:
            self.next_sync = 10
            self.buildings = Group()

    @property
    def current_player(self) -> PlayerInfo:
        return self.get_player(self.current_team)

    def get_player(self, team_id: int) -> PlayerInfo:
        for p in self.players:
            if p.team_id == team_id:
                return p
        raise IndexError(f'No player with {team_id=}')

    def update(self, event: pygame.event) -> None:
        self.camera.update(event)
        self.sprites.update(event)

        if self.side == Game.Side.SERVER and event.type == EVENT_SEC:
            self.next_sync -= 1
            if self.next_sync <= 0:
                self.next_sync = 10
                self.sync_all_clients()

    def draw(self, screen: Surface) -> None:
        for unit in self.sprites:
            unit.draw(screen, self.camera)
        self.camera.draw_center(screen)

    def find_with_id(self, unit_id: int) -> Unit:
        unit: Unit
        for unit in self.sprites:
            if unit.unit_id == unit_id:
                return unit

    @_side_only(Side.SERVER)
    def set_target(self, unit: Unit, target: Tuple[Fighter.Target, Any]):
        unit.target = target
        self.send([Game.ClientCommands.TARGET_CHANGE, unit.unit_id, unit.encode_target()])

    @_side_only(Side.SERVER)
    def sync_all_clients(self):
        print('Sync')
        unit: Unit
        for unit in self.sprites:
            self.send([Game.ClientCommands.UPDATE, unit.name, unit.unit_id, unit.team, unit.get_update_args()])

    @_side_only(Side.SERVER)
    def create_unit(self, name: str, pos: tuple[float, float], team_id: int = -1, **kwargs):
        cls = self.get_base_class(name)
        unit = cls(self, name, pos[0], pos[1], UniqueIdGenerator.generate_id(), team_id)
        for key, arg in kwargs.items():
            setattr(unit, key, arg)
        if 'buildable' in unit.cls_dict['tags']:
            self.buildings.add(unit)

        self.sprites.add(unit)
        self.send([Game.ClientCommands.CREATE, unit.name, unit.unit_id, team_id, unit.get_update_args()])

    @_side_only(Side.SERVER)
    def delete_unit(self, unit: Unit):
        self.sprites.remove(unit)
        if unit in self.buildings:
            self.buildings.remove(unit)
        unit.dead = True
        self.send([Game.ClientCommands.DEAD, unit.unit_id])

    @_side_only(Side.SERVER)
    def place_unit(self, name: str, pos: tuple[float, float], team_id=-1):
        prefab = self.mod_loader.entities[name]
        if 'buildable' not in prefab['tags']:
            print(f'Trying to place non placeable: {name=}, {team_id=}')
            return

        spr = Sprite()
        rect = Rect((0, 0), prefab['size'])
        rect.center = pos
        spr.rect = rect
        if pygame.sprite.spritecollideany(spr, self.sprites):
            print(f'Trying to place on occupied area: {name=}, {team_id=}')
            return

        player = self.get_player(team_id)
        if not player.has_enough(RequiredCost(**prefab['cost'])):
            print(f'Trying to place without resources: {name=}, {team_id=}')
            return

        cls = self.mod_loader.bases[prefab['base']]
        unit = cls(self, name, pos[0], pos[1], UniqueIdGenerator.generate_id(), team_id)  # todo remove this shit
        unit.unit_id = UniqueIdGenerator.generate_id()
        self.sprites.add(unit)
        self.buildings.add(unit)

        player.spend(RequiredCost(**prefab['cost']))
        self.send([Game.ClientCommands.CREATE, unit.name, unit.unit_id, team_id, unit.get_update_args()])
        self.update_player_info(player)

    @_side_only(Side.CLIENT)
    def load_unit(self, args: list[Any]) -> None:
        cls = self.get_base_class(args[0])
        u = cls(self, args[0], 0, 0, args[1], args[2])
        u.set_update_args(args[3])
        self.sprites.add(u)

    def send(self, command: list[Any], player_id: Optional[int] = None) -> None:
        if player_id == -1:
            return
        self.send_connection.send((command, player_id))

    @_side_only(Side.CLIENT)
    def place_building(self, entity_name: str, pos: tuple[float, float]) -> None:
        self.send([Game.ServerCommands.PLACE_UNIT, entity_name,
                   int(pos[0] - self.camera.offset_x),
                   int(pos[1] - self.camera.offset_y)])

    def get_base_class(self, name: str) -> Type[Unit]:
        return self.mod_loader.bases[self.mod_loader.entities[name]['base']]

    def collide_cursor(self, cursor_pos) -> list[Unit]:
        cursor = Sprite()
        cursor.rect = Rect((int(cursor_pos[0] - self.camera.offset_x), int(cursor_pos[1] - self.camera.offset_y)),
                           (1, 1))
        return pygame.sprite.spritecollide(cursor, self.sprites, False)

    def update_health_info(self, unit: Unit) -> None:
        self.send([Game.ClientCommands.HEALTH_INFO, unit.unit_id, unit.health, unit.max_health])

    def update_player_info(self, player_info: PlayerInfo) -> None:
        self.send([Game.ClientCommands.RESOURCE_INFO, {
            'money': player_info.resources.money,
            'wood': player_info.resources.wood
        }], player_info.team_id)


class ModLoader:
    def __init__(self):
        self.funcs = {}
        self.entities = {}
        self.mod_dict = {}
        self.bases = {
            'unit': Unit,
            'twist_unit': TwistUnit,
            'fighter': Fighter,
            'producing_building': ProducingBuilding,
            'projectile': Projectile,
        }

    def mod_load_list(self):
        return os.listdir('mods')

    def decode_json(self, dct, mod_name):
        if value := dct.get('__func__'):
            return self.funcs[value]
        if value := dct.get('__path__'):
            return f'mods/{mod_name}/assets/{value}'
        if value := dct.get('__color__'):
            return Color(*value)
        return dct

    def import_mods(self):
        mods = self.mod_load_list()

        print('Mod loader function importing...')
        for m in mods:
            __import__(f'mods.{m}')
        print('Mod loader function import ended')

        for m in mods:
            self.load_mod(m)

        print('Mods installed:')
        for name, version in self.mod_dict.items():
            print(f'{name=}, {version=}')
        print('Mod initialization completed')

    def load_mod(self, name):
        with open(f'mods/{name}/init.json', mode='r', encoding='utf8') as json_file:
            mod_json = json.load(json_file, object_hook=lambda x: self.decode_json(x, name))
        self.mod_dict[mod_json['name']] = mod_json['version']
        try:
            self.entities.update(mod_json['entities'])
        except KeyError:
            pass

    def load_func(self, name):
        def load_func_dec(func):
            print(f'Found function "{name}": {func.__name__}')
            self.funcs[name] = func
            return func

        return load_func_dec
