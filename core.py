import json
import math
import os
import random
from enum import Enum, auto
from functools import wraps
from typing import Tuple, Any, Type

import pygame
from pygame import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite

from config import config
from constants import EVENT_UPDATE, EVENT_SEC
from ui import UIElement


class Camera:
    def __init__(self, game):
        self.offset_x = config['screen']['size'][0] / 2
        self.offset_y = config['screen']['size'][1] / 2
        self.game = game
        self.speed = 1

    def update(self, event):
        if event.type == EVENT_UPDATE:
            keys = pygame.key.get_pressed()
            x_change, y_change = 0, 0
            if keys[pygame.K_d]:
                x_change -= 1
            if keys[pygame.K_a]:
                x_change += 1
            if keys[pygame.K_s]:
                y_change -= 1
            if keys[pygame.K_w]:
                y_change += 1
            self.move(x_change, y_change)
            if x_change != 0 or y_change != 0:
                self.speed += config['camera']['step_faster']
                self.speed = min(config['camera']['max_speed'], self.speed)
            else:
                self.speed -= config['camera']['step_slower']
                self.speed = max(config['camera']['min_speed'], self.speed)

    def move(self, x, y):
        self.offset_x += x * self.speed
        self.offset_y += y * self.speed
        if self.offset_x < -self.game.world_size + config['screen']['size'][0]:
            self.offset_x = -self.game.world_size + config['screen']['size'][0]
        if self.offset_x > self.game.world_size:
            self.offset_x = self.game.world_size
        if self.offset_y < -self.game.world_size + config['screen']['size'][1]:
            self.offset_y = -self.game.world_size + config['screen']['size'][1]
        if self.offset_y > self.game.world_size:
            self.offset_y = self.game.world_size

    @property
    def center(self):
        return self.offset_x, self.offset_y

    def draw_center(self, screen):
        c = self.center
        pygame.draw.line(screen, Color('red3'), c, (self.offset_x + 15, self.offset_y), 3)
        pygame.draw.line(screen, Color('green'), c, (self.offset_x, self.offset_y + 15), 3)
        pygame.draw.line(screen, Color('blue'), c, (self.offset_x - 8, self.offset_y - 8), 4)


class Unit(Sprite):
    next_id = 0

    def __init__(self, game, name, x, y, team=-1):
        self.name = name
        self.game = game
        self.cls_dict = self.game.mod_loader.entities[name]
        self.pos = Vector2()
        self.pos.xy = x, y
        self.texture = pygame.image.load(self.cls_dict['texture'].format(team='green'))
        self.rect: Rect = self.texture.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.team = team
        if game.side == Game.Side.SERVER:
            self.unit_id = Unit.next_id
            Unit.next_id += 1
        super().__init__()

    def update(self, event):
        pass

    def move(self, x, y):
        self.pos.x += x
        self.pos.y += y
        self.rect.center = self.pos.x, self.pos.y

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, value):
        self.pos.x = value[0]
        self.pos.y = value[1]
        self.rect.center = self.pos.x, self.pos.y

    def draw(self, screen, camera):
        screen.blit(self.texture, self.rect.move(camera.offset_x, camera.offset_y))

    def get_update_args(self):
        return [int(self.pos.x), int(self.pos.y)]

    def set_update_args(self, args):
        self.center = int(args[0]), int(args[1])


class TwistUnit(Unit):
    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self._angle = 0
        self.rot_texture = self.texture
        self.img_rect: Rect = self.rot_texture.get_rect()
        self.angle = 0

    def update(self, event):
        super().update(event)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        while value >= 360:
            value -= 360
        while value < 0:
            value += 360
        self._angle = value
        self.update_image()

    def move(self, x, y):
        super().move(x, y)
        self.img_rect.center = self.rect.center

    def update_image(self):
        self.rot_texture = pygame.transform.rotate(self.texture, -self._angle)
        self.img_rect = self.rot_texture.get_rect()
        self.img_rect.center = self.rect.center

    def draw(self, screen, camera):
        screen.blit(self.rot_texture, self.img_rect.move(camera.offset_x, camera.offset_y))

    def get_update_args(self):
        args = super().get_update_args()
        args.append(int(self._angle))
        return args

    def set_update_args(self, args):
        super().set_update_args(args)
        self.angle = int(args[2])


class Fighter(TwistUnit):
    class Target(Enum):
        NONE = 'none'
        ATTACK = 'attack'
        MOVE = 'move'

    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self.target_angle = 0
        self.target: Tuple[Fighter.Target, Any] = (Fighter.Target.NONE, None)
        self.delay = 0
        self.delay_time = self.cls_dict['delay_time']
        self.damage = self.cls_dict.get('damage', 0)
        self.speed = self.cls_dict['speed']
        self.angle_speed = self.cls_dict['angle_speed']
        self.attack_range = self.cls_dict['attack_range']

    def find_new_target(self):
        pass

    def update_delay(self):
        if self.game.side is Game.Side.SERVER:
            self.delay -= 1

    def update(self, event):
        if (event.type == EVENT_SEC) and (self.game.side is Game.Side.SERVER):
            if self.target[0] is Fighter.Target.NONE:
                self.find_new_target()
        if event.type == EVENT_UPDATE:
            if self.target[0] is Fighter.Target.ATTACK:
                self.find_target_angle()
                self.turn_around()
                self.update_delay()
                if self.is_close_to_target():
                    self.single_attack()
                else:
                    self.move_to_angle()
            elif self.target[0] == Fighter.Target.MOVE:
                self.move_to_point()

    def find_target_angle(self):
        self.target_angle = int(math.degrees(math.atan2(self.target[1].y - self.pos.y, self.target[1].x - self.pos.x)))
        if self.target_angle < 0:
            self.target_angle += 360

    def is_close_to_target(self):
        pass

    def turn_around(self):
        angle_diff = self.target_angle - self.angle
        if angle_diff == 0:
            return

        speed = min(self.angle_speed, abs(angle_diff))

        if angle_diff < 0:
            if abs(angle_diff) >= 180:
                self.angle += speed
            else:
                self.angle -= speed
        elif angle_diff > 0:
            if abs(angle_diff) >= 180:
                self.angle -= speed
            else:
                self.angle += speed

    def single_attack(self):
        pass

    def move_to_angle(self):
        self.move(math.cos(math.radians(self.angle)) * self.speed, math.sin(math.radians(self.angle)) * self.speed)

    def move_to_point(self):
        self.find_target_angle()
        self.turn_around()
        self.move_to_angle()
        if self.game.side is Game.Side.SERVER:
            if self.pos.distance_to(self.target[1]) <= 5:
                self.game.set_target(self, (Fighter.Target.NONE, None))

    def encode_target(self):
        if self.target[0] is Fighter.Target.NONE:
            return self.target[0].value

        elif self.target[0] is Fighter.Target.MOVE:
            return f'{self.target[0].value}_{self.target[1][0]}_{self.target[1][1]}'

        elif self.target[0] is Fighter.Target.ATTACK:
            return f'{self.target[0].value}_{self.target[1].unit_id}'

    def decode_target(self, arg):
        args = arg.split('_')

        if args[0] == Fighter.Target.NONE.value:
            return Fighter.Target.NONE, None

        if args[0] == Fighter.Target.MOVE.value:
            return Fighter.Target.MOVE, (Vector2(float(args[1]), float(args[2])))

        if args[0] == Fighter.Target.ATTACK.value:
            return Fighter.Target.ATTACK, self.game.find_with_id(int(args[1]))


class ProducingBuilding(Unit):
    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self.units_tray = []
        self.valid_types = self.cls_dict['valid_types']


def side_only(side):
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
        CREATE = '1'
        UPDATE = '2'
        TARGET_CHANGE = '3'

    class ServerCommands:
        """Команды, отправляемые серверу"""
        PLACE_UNIT = '1'
        SET_TARGET_MOVE = '2'

    def __init__(self, side: Side, mod_loader, send_connection, nicks, connection_list=None):
        self.mod_loader = mod_loader
        self.side = side
        self.sprites = Group()
        self.world_size = config['world']['size']
        self.world_rect = Rect(-self.world_size, -self.world_size, self.world_size * 2, self.world_size * 2)
        self.send_connection = send_connection
        self.camera = Camera(self)
        if self.side == Game.Side.SERVER:
            self.next_sync = 10
            self.connection_list = connection_list

    def update(self, event):
        self.camera.update(event)
        self.sprites.update(event)

        if self.side == Game.Side.SERVER:
            if event.type == EVENT_SEC:
                self.next_sync -= 1
                if random.randint(0, 100) < 25:
                    self.create_unit('warrior')
                    print('Created')
                if self.next_sync <= 0:
                    self.next_sync = 10
                    self.sync()
        elif self.side == Game.Side.CLIENT:
            if event.type == pygame.MOUSEBUTTONUP:
                for unit in self.sprites:
                    if isinstance(unit, Fighter):
                        self.send_connection.send(
                            f'{Game.ServerCommands.SET_TARGET_MOVE}~{unit.unit_id}~{int(event.pos[0] - self.camera.offset_x + random.randint(-75, 75))}~{int(event.pos[1] - self.camera.offset_y + random.randint(-75, 75))}')

                self.send_connection.send(
                    f'{Game.ServerCommands.PLACE_UNIT}~{"archer"}~{int(event.pos[0] - self.camera.offset_x)}~{int(event.pos[1] - self.camera.offset_y)}')

    def draw(self, screen):
        for unit in self.sprites:
            unit.draw(screen, self.camera)
        self.camera.draw_center(screen)

    def find_with_id(self, unit_id: int):
        for u in self.sprites:
            if u.unit_id == unit_id:
                return u

    @side_only(Side.SERVER)
    def set_target(self, unit, target: Tuple[Fighter.Target, Any]):
        unit.target = target
        self.send_connection.send(f'{Game.ClientCommands.TARGET_CHANGE}~{unit.unit_id}~{unit.encode_target()}')

    @side_only(Side.SERVER)
    def sync(self):
        print('Sync')
        for unit in self.sprites:
            send_msg = f'{Game.ClientCommands.UPDATE}~{unit.name}~{unit.unit_id}~{"~".join(map(str, unit.get_update_args()))}'
            self.send_connection.send(send_msg)

    @side_only(Side.SERVER)
    def create_unit(self, name, pos=None):
        if not pos:
            pos = (random.randint(-self.world_size, self.world_size),
                   random.randint(-self.world_size, self.world_size))
        cls = self.get_base_class(name)
        u = cls(self, name, pos[0], pos[1])
        self.sprites.add(u)
        self.send_connection.send(
            f'{Game.ClientCommands.CREATE}~{u.name}~{u.unit_id}~{"~".join(map(str, u.get_update_args()))}')

    @side_only(Side.CLIENT)
    def load_unit(self, args):
        cls = self.get_base_class(args[0])
        u = cls(self, args[0], 0, 0)
        u.unit_id = int(args[1])
        u.set_update_args(args[2:])
        self.sprites.add(u)

    def get_base_class(self, name):
        return self.mod_loader.bases[self.mod_loader.entities[name]['base']]

    def handle_command(self, command, args, sender=None):
        if self.side == Game.Side.CLIENT:
            print(command, args)
            if command == Game.ClientCommands.CREATE:
                self.load_unit(args)

            elif command == Game.ClientCommands.UPDATE:
                unit = self.find_with_id(int(args[1]))
                if unit is not None:
                    unit.set_update_args(args[2:])
                else:
                    self.load_unit(args)
            elif command == Game.ClientCommands.TARGET_CHANGE:
                unit = self.find_with_id(int(args[0]))
                unit.target = unit.decode_target(args[1])
            else:
                print('Unexpected command', command, args)
        elif self.side == Game.Side.SERVER:
            print(command, args)
            if command == Game.ServerCommands.PLACE_UNIT:
                self.create_unit('archer', (int(args[1]), int(args[2])))
            elif command == Game.ServerCommands.SET_TARGET_MOVE:
                unit = self.find_with_id(int(args[0]))
                self.set_target(unit, (Fighter.Target.MOVE, Vector2(float(args[1]), float(args[2]))))
            else:
                print('Unexpected command', command, args)


class Minimap(UIElement):
    def __init__(self, game: Game):
        self.game = game
        self.mark_size = config['minimap']['mark_size']
        self.mark_color = Color(*config['minimap']['mark_color'])
        super().__init__(Rect(*config['minimap']['bounds']), None)

    def draw(self, screen):
        super().draw(screen)
        mark_rect = Rect(self.absolute_bounds.x, self.absolute_bounds.y, self.mark_size, self.mark_size)
        for unit in self.game.sprites:
            pos = self.worldpos_to_minimap(unit.pos.x, unit.pos.y)
            mark_rect.centerx = self.absolute_bounds.x + pos[0]
            mark_rect.centery = self.absolute_bounds.y + pos[1]
            pygame.draw.ellipse(screen, self.mark_color, mark_rect)

        camera_rect = Rect(
            (self.game.world_size - self.game.camera.offset_x) * self.world_ratio_width,
            (self.game.world_size - self.game.camera.offset_y) * self.world_ratio_height,
            config['screen']['size'][0] * self.world_ratio_width,
            config['screen']['size'][1] * self.world_ratio_height
        )
        pygame.draw.rect(screen, Color('yellow'), camera_rect.move(self.absolute_bounds.x, self.absolute_bounds.y), 1)

    def worldpos_to_minimap(self, x, y):
        return (x + self.game.world_size) * self.world_ratio_width, \
               (y + self.game.world_size) * self.world_ratio_height

    @property
    def world_ratio_width(self):
        return self.relative_bounds.width / (2 * self.game.world_size)

    @property
    def world_ratio_height(self):
        return self.relative_bounds.height / (2 * self.game.world_size)

    def minimap_to_worldpos(self, x, y):
        raise Exception('Not supported')


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
        }

    def mod_load_list(self):
        return os.listdir('mods')

    def decode_json(self, dct, mod_name):
        if value := dct.get('__func__'):
            return self.funcs[value]
        if value := dct.get('__path__'):
            return f'mods/{mod_name}/assets/{value}'
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
