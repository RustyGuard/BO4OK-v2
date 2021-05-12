import json
import math
import os
import random
from enum import Enum, auto
from functools import wraps
from typing import Tuple, Any, Optional, List

import pygame
from pygame import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite

from config import config
from constants import EVENT_UPDATE, EVENT_SEC
from ui import UIElement, UIButton, UIImage, Label


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

    def __init__(self, game, name, x, y, team):
        self.name = name
        self.game = game
        self.cls_dict = self.game.mod_loader.entities[name]
        self.pos = Vector2()
        self.pos.xy = x, y
        self.texture = pygame.image.load(self.cls_dict['texture'].format(team=self.game.get_player(team).color_name))
        self.rect: Rect = self.texture.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.team = team
        self.team_color = self.game.get_player(team).color
        self.max_health = self.cls_dict.get('max_health', 1)
        self.health = self.max_health
        self.dead = False
        if game.side == Game.Side.SERVER:
            self.unit_id = Unit.next_id
            Unit.next_id += 1
            print('next id', Unit.next_id)
        super().__init__()

    @property
    def x(self):
        return self.rect.centerx

    @property
    def y(self):
        return self.rect.centery

    def update(self, event):
        pass

    def move(self, x, y):
        self.pos.x += x
        self.pos.y += y
        self.rect.center = self.pos.x, self.pos.y

    @property
    def pos_around(self):
        return Vector2(self.pos.x + random.randint(-150, 150), self.pos.y + random.randint(-150, 150))

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, value):
        self.pos.x = value[0]
        self.pos.y = value[1]
        self.rect.center = self.pos.x, self.pos.y

    def draw_health_bar(self, screen, target_rect):
        if self.health != self.max_health:
            health_rect = Rect(0, 0, 25, 7)
            health_rect.bottom = target_rect.top - 2
            health_rect.centerx = target_rect.centerx
            pygame.draw.rect(screen, Color('gray'), health_rect)
            health_rect.width *= self.health / self.max_health
            pygame.draw.rect(screen, Color('red'), health_rect)

    def draw(self, screen, camera):
        draw_rect = self.rect.move(camera.offset_x, camera.offset_y)
        screen.blit(self.texture, draw_rect)
        self.draw_health_bar(screen, draw_rect)

    def get_update_args(self):
        return [int(self.pos.x), int(self.pos.y), int(self.health), int(self.max_health)]

    def set_update_args(self, args):
        self.center = args.pop(0), args.pop(0)
        self.health = float(args.pop(0))
        self.max_health = float(args.pop(0))

    def take_damage(self, dmg):
        if 'invincible' in self.cls_dict['tags']:
            print('What are you trying to do? It is freaking invincible')
            return
        self.health -= dmg
        if self.health <= 0:
            self.game.delete_unit(self)
            return
        self.game.send([Game.ClientCommands.HEALTH_INFO, self.unit_id, self.health, self.max_health])


class TwistUnit(Unit):
    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self._angle = 0
        self.rot_texture = self.texture
        self.img_rect: Rect = self.rot_texture.get_rect()
        self.angle = 0

    def update(self, event):
        super().update(event)
        if 'update' in self.cls_dict:
            self.cls_dict['update'](self, event)

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
        target_rect = self.img_rect.move(camera.offset_x, camera.offset_y)
        screen.blit(self.rot_texture, target_rect)
        self.draw_health_bar(screen, target_rect)

    def move_to_angle(self):
        speed = self.cls_dict['speed']
        self.move(math.cos(math.radians(self.angle)) * speed, math.sin(math.radians(self.angle)) * speed)

    def get_update_args(self):
        args = super().get_update_args()
        args.append(int(self._angle))
        return args

    def set_update_args(self, args):
        super().set_update_args(args)
        self.angle = args.pop(0)


class Projectile(TwistUnit):
    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self.lifetime = self.cls_dict['lifetime']
        self.damage = self.cls_dict.get('damage', 0)

    def update(self, event):
        super().update(event)
        if event.type == EVENT_UPDATE:
            self.move_to_angle()
            if self.game.side == Game.Side.SERVER:
                self.lifetime -= 1
                if self.lifetime <= 0:
                    self.game.delete_unit(self)
                    return
                for unit in pygame.sprite.spritecollide(self, self.game.sprites, False):
                    if unit != self and unit.team != self.team and 'invincible' not in unit.cls_dict['tags']:
                        unit.take_damage(self.damage)
                        self.game.delete_unit(self)
                        return


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
        self.angle_speed = self.cls_dict['angle_speed']
        self.attack_range = self.cls_dict['attack_range']

    def find_new_target(self):
        nearest, dist = None, math.inf
        for unit in self.game.sprites:
            if unit != self and 'invincible' not in unit.cls_dict['tags'] and self.valid_target(unit):
                d = self.pos.distance_to(unit.pos)
                if d < dist:
                    nearest, dist = unit, d
        if nearest is not None:
            self.game.set_target(self, (Fighter.Target.ATTACK, nearest))

    def update_delay(self):
        if self.game.side is Game.Side.SERVER:
            self.delay -= 1

    def update(self, event):
        super().update(event)
        if (event.type == EVENT_SEC) and (self.game.side is Game.Side.SERVER):
            if self.target[0] is Fighter.Target.NONE:
                self.find_new_target()
        if event.type == EVENT_UPDATE:
            if self.target[0] is Fighter.Target.ATTACK:
                if self.game.side == Game.Side.SERVER and self.target[1].dead:
                    self.game.set_target(self, (Fighter.Target.NONE, None))
                    self.find_new_target()
                    return

                self.find_target_angle()
                self.turn_around()
                self.update_delay()
                if self.is_close_to_target():
                    self.cls_dict['when_close'](self)
                else:
                    self.move_to_angle()
            elif self.target[0] == Fighter.Target.MOVE:
                self.move_to_point()

    def find_target_angle(self):
        self.target_angle = int(math.degrees(math.atan2(self.target[1].y - self.pos.y, self.target[1].x - self.pos.x)))
        if self.target_angle < 0:
            self.target_angle += 360

    def is_close_to_target(self):
        return self.pos.distance_to(self.target[1].pos) < self.attack_range

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
        if self.game.side is Game.Side.SERVER:
            if self.delay <= 0:
                self.delay = self.delay_time

                self.target[1].take_damage(self.damage)

    def throw_projectile(self, name):
        if self.game.side is Game.Side.SERVER:
            if self.delay <= 0:
                self.game.create_unit(name, (self.x, self.y), self.team, angle=self.angle)
                self.delay = self.delay_time

    def move_to_point(self):
        self.find_target_angle()
        self.turn_around()
        self.move_to_angle()
        if self.game.side is Game.Side.SERVER:
            if self.pos.distance_to(self.target[1]) <= 5:
                self.game.set_target(self, (Fighter.Target.NONE, None))

    def encode_target(self):
        if self.target[0] is Fighter.Target.NONE:
            return [self.target[0].value]

        elif self.target[0] is Fighter.Target.MOVE:
            return [self.target[0].value, self.target[1][0], self.target[1][1]]

        elif self.target[0] is Fighter.Target.ATTACK:
            return [self.target[0].value, self.target[1].unit_id]

    def decode_target(self, args):
        if args[0] == Fighter.Target.NONE.value:
            return Fighter.Target.NONE, None

        if args[0] == Fighter.Target.MOVE.value:
            return Fighter.Target.MOVE, (Vector2(args[1], args[2]))

        if args[0] == Fighter.Target.ATTACK.value:
            print(args[1])
            return Fighter.Target.ATTACK, self.game.find_with_id(args[1])

    def valid_target(self, unit):
        return self.cls_dict['valid_target'](self, unit)


class ProducingBuilding(Unit):
    def __init__(self, game, name, x, y, team=-1):
        super().__init__(game, name, x, y, team)
        self.valid_types = self.cls_dict['valid_types']
        self.produce_time = self.cls_dict['produce_time']
        self.time = self.produce_time
        self.units_tray = []

    def add_to_queque(self, name):
        if name not in self.cls_dict['valid_types']:
            print(f'{self.unit_id} can not produce {name}')
            return
        print(self.game.get_player(self.team))
        self.game.get_player(self.team).spend({'money': 2})
        self.units_tray.append(name)
        print(self.units_tray)

    def update(self, event):
        super().update(event)

        if self.game.side is Game.Side.SERVER and event.type == EVENT_SEC and self.units_tray:
            if self.time > 0:
                self.time -= 1
            elif self.time == 0:
                unit = self.units_tray.pop(0)
                self.time = self.produce_time
                self.game.create_unit(unit, self.pos_around, self.team)
                print('created')


def side_only(side):
    def side_only_dec(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.side != side:
                raise Exception(f'No supported on {self.side}')
            return func(self, *args, **kwargs)

        return wrapper

    return side_only_dec


class Player:
    color_list = {
        'aqua': Color('aquamarine'),
        'blue': Color('blue'),
        'green': Color('green'),
        'light_green': Color('green2'),
        'orange': Color('orange'),
        'pink': Color('pink'),
        'purple': Color('purple'),
        'red': Color('red'),
        'yellow': Color('yellow'),
        'black': Color('black')
    }

    def __init__(self, game, player_info):
        self.game = game
        self.team_id = player_info['team_id']
        self.color_name = player_info['color']
        self.color = Player.color_list[self.color_name]
        self.nick = player_info['nick']
        self.wood = player_info['wood']
        self.money = player_info['money']
        self.meat = player_info['meat']
        self.base_meat = player_info['base_meat']
        self.max_meat = player_info['base_meat']

    def has_enough(self, cost):
        if self.money < cost.get('money', 0):
            return False
        if self.wood < cost.get('wood', 0):
            return False
        return True

    def spend(self, cost):
        print(cost)
        to_update = {}
        money = cost.get('money', 0)
        if money > 0:
            self.money -= money
            to_update['money'] = self.money
        wood = cost.get('wood', 0)
        if wood > 0:
            self.wood -= wood
            to_update['wood'] = self.wood
        print(to_update)
        self.game.send([Game.ClientCommands.RESOURCE_INFO, to_update], self.team_id)


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

    def __init__(self, side: Side, mod_loader, send_connection, players_list: List, current_team: int,
                 connection_list=None):
        self.mod_loader = mod_loader
        self.side = side
        self.sprites = Group()
        self.world_size = config['world']['size']
        self.world_rect = Rect(-self.world_size, -self.world_size, self.world_size * 2, self.world_size * 2)
        self.send_connection = send_connection
        self.camera = Camera(self)

        self.players = []
        for player_info in players_list:
            player = Player(self, player_info)
            self.players.append(player)
        self.players.append(Player(self,
                                   {'team_id': -1, 'color': 'black',
                                    'nick': 'Admin', 'money': 50000,
                                    'wood': 50000, 'meat': 0, 'base_meat': 50000}))
        self.current_team = current_team

        if self.side == Game.Side.SERVER:
            self.next_sync = 10
            self.connection_list = connection_list
            self.buildings = Group()

    @property
    def current_player(self) -> Player:
        return self.get_player(self.current_team)

    def get_player(self, team_id) -> Player:
        for p in self.players:
            if p.team_id == team_id:
                return p
        raise IndexError(f'No player with {team_id=}')

    def update(self, event):
        self.camera.update(event)
        self.sprites.update(event)

        if self.side == Game.Side.SERVER:
            if event.type == EVENT_SEC:
                self.next_sync -= 1
                if self.next_sync <= 0:
                    self.next_sync = 10
                    self.sync()

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
        self.send([Game.ClientCommands.TARGET_CHANGE, unit.unit_id, unit.encode_target()])

    @side_only(Side.SERVER)
    def sync(self):
        print('Sync')
        for unit in self.sprites:
            self.send([Game.ClientCommands.UPDATE, unit.name, unit.unit_id, unit.team, unit.get_update_args()])

    @side_only(Side.SERVER)
    def create_unit(self, name, pos, team_id=-1, **kwargs):
        cls = self.get_base_class(name)
        u = cls(self, name, pos[0], pos[1], team_id)
        for key, arg in kwargs.items():
            setattr(u, key, arg)
        if 'buildable' in u.cls_dict['tags']:
            self.buildings.add(u)
        self.sprites.add(u)
        self.send([Game.ClientCommands.CREATE, u.name, u.unit_id, team_id, u.get_update_args()])

    @side_only(Side.SERVER)
    def delete_unit(self, unit):
        self.sprites.remove(unit)
        if unit in self.buildings:
            self.buildings.remove(unit)
        unit.dead = True
        self.send([Game.ClientCommands.DEAD, unit.unit_id])

    @side_only(Side.SERVER)
    def place_unit(self, name, pos, team_id=-1):
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

        pl = self.get_player(team_id)
        if not pl.has_enough(prefab['cost']):
            print(f'Trying to place without resources: {name=}, {team_id=}')
            return

        cls = self.mod_loader.bases[prefab['base']]
        u = cls(self, name, pos[0], pos[1], team_id)
        self.sprites.add(u)
        self.buildings.add(u)

        pl.spend(prefab['cost'])
        self.send([Game.ClientCommands.CREATE, u.name, u.unit_id, team_id, u.get_update_args()])

    @side_only(Side.CLIENT)
    def load_unit(self, args):
        cls = self.get_base_class(args[0])
        u = cls(self, args[0], 0, 0, args[2])
        u.unit_id = args[1]
        u.set_update_args(args[3])
        self.sprites.add(u)

    def send(self, command: list, player_id: Optional[int] = None):
        if player_id == -1:
            return
        self.send_connection.send((command, player_id))

    @side_only(Side.CLIENT)
    def place_building(self, entity_name, pos):
        self.send([Game.ServerCommands.PLACE_UNIT, entity_name,
                   int(pos[0] - self.camera.offset_x),
                   int(pos[1] - self.camera.offset_y)])

    def get_base_class(self, name):
        return self.mod_loader.bases[self.mod_loader.entities[name]['base']]

    def collide_cursor(self, cursor_pos):
        cursor = Sprite()
        cursor.rect = Rect((int(cursor_pos[0] - self.camera.offset_x), int(cursor_pos[1] - self.camera.offset_y)),
                           (1, 1))
        return pygame.sprite.spritecollide(cursor, self.sprites, False)

    def handle_command(self, command, args, sender=None):
        if self.side == Game.Side.CLIENT:
            print(command, args)
            if command == Game.ClientCommands.CREATE:
                self.load_unit(args)

            elif command == Game.ClientCommands.UPDATE:
                unit = self.find_with_id(args[1])
                if unit is not None:
                    unit.set_update_args(args[3])
                else:
                    print('\t[ALERT] It is ghoust! I am scared!', args)
                    self.load_unit(args)

            elif command == Game.ClientCommands.TARGET_CHANGE:
                unit = self.find_with_id(args[0])
                unit.target = unit.decode_target(args[1])
            elif command == Game.ClientCommands.TARGET_CHANGE:
                unit = self.find_with_id(args[0])
                unit.target = unit.decode_target(args[1])

            elif command == Game.ClientCommands.RESOURCE_INFO:
                pl = self.current_player
                for attr in ['meat', 'money', 'wood', 'max_meat']:
                    if val := args[0].get(attr, None):
                        setattr(pl, attr, val)

            elif command == Game.ClientCommands.HEALTH_INFO:
                unit = self.find_with_id(args[0])
                unit.health = float(args[1])
                unit.max_health = float(args[2])

            elif command == Game.ClientCommands.DEAD:
                unit = self.find_with_id(args[0])
                self.sprites.remove(unit)
                print(unit, args[0], 'dead')

            else:
                print('Unexpected command', command, 'args:', args)
        elif self.side == Game.Side.SERVER:
            print(command, args, sender)
            if command == Game.ServerCommands.PLACE_UNIT:
                self.place_unit(args[0], (args[1], args[2]), sender)

            elif command == Game.ServerCommands.SET_TARGET_MOVE:
                unit = self.find_with_id(args[0])
                self.set_target(unit, (Fighter.Target.MOVE, Vector2(args[1], args[2])))

            elif command == Game.ServerCommands.PRODUCE_UNIT:
                prod_build = self.find_with_id(args[0])
                unit_name = args[1]

                try:
                    prod_build.add_to_queque(unit_name)
                except AttributeError:
                    print(f'add_to_queque not provided to {prod_build.__class__.__name__}')

            else:
                print('Unexpected command', command, args)


class Minimap(UIElement):
    def __init__(self, game: Game):
        self.game = game
        self.mark_size = config['minimap']['mark_size']
        self.mark_color = config['minimap']['mark_color']
        print(self.mark_color)
        super().__init__(Rect(*config['minimap']['bounds']), None)

    def draw(self, screen):
        super().draw(screen)
        mark_rect = Rect(self.absolute_bounds.x, self.absolute_bounds.y, self.mark_size, self.mark_size)
        for unit in self.game.sprites:
            shape = unit.cls_dict.get('mark_shape', 'quad')

            pos = self.worldpos_to_minimap(unit.pos.x, unit.pos.y)
            mark_rect.centerx = self.absolute_bounds.x + pos[0]
            mark_rect.centery = self.absolute_bounds.y + pos[1]

            if shape == 'circle':
                pygame.draw.ellipse(screen, self.mark_color, mark_rect)
                pygame.draw.ellipse(screen, unit.team_color, mark_rect, 2)
            if shape == 'quad':
                pygame.draw.rect(screen, self.mark_color, mark_rect)
                pygame.draw.rect(screen, unit.team_color, mark_rect, 3)

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


class BuildMenu(UIElement):
    class BuildMenuItem:
        def __init__(self, name, entity_json, game):
            self.entity_json = entity_json
            self.game = game
            self.name = name
            self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            self.icon = pygame.image.load(self.entity_json['icon'].format(team=self.game.current_player.color_name))

    def __init__(self, bounds, game):
        super().__init__(bounds, None)
        self.selected = None
        self.game = game
        self.buildings = {}
        i = 0
        for name, entity in self.game.mod_loader.entities.items():
            if 'buildable' in entity['tags']:
                self.buildings[name] = BuildMenu.BuildMenuItem(name, entity, game)
                btn = UIButton(Rect(0, i * 55 + 15, 50, 50), None, self.select, name)
                btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, self.buildings[name].icon))
                self.append_child(btn)
                i += 1

    def draw(self, screen):
        if self.selected:
            r = self.selected.icon.get_rect()
            r.center = pygame.mouse.get_pos()
            screen.blit(self.selected.icon, r)
        super().draw(screen)

    def update(self, event):
        if super().update(event):
            return True
        if self.selected:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.game.place_building(self.selected.name, pygame.mouse.get_pos())
                    return True
                if event.button == 3:
                    self.selected = None
                    return True
        return False

    def select(self, item_id):
        self.selected = self.buildings[item_id] if (item_id is not None) else None


class ProduceMenu(UIElement):
    class ProduceMenuItem:
        def __init__(self, name, entity_json, game):
            self.entity_json = entity_json
            self.game = game
            self.name = name
            self.color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            self.icon = pygame.image.load(self.entity_json['icon'].format(team=self.game.current_player.color_name))

    def __init__(self, bounds, game):
        super().__init__(bounds, None)
        self.game = game
        self.units = {}

    def set_selected(self, unit):
        i = 0
        self.childs.clear()
        for name in unit.cls_dict['valid_types']:
            entity = self.game.mod_loader.entities[name]
            self.units[name] = ProduceMenu.ProduceMenuItem(name, entity, self.game)
            btn = UIButton(Rect(150, i * 30 + 15, 25, 25), None, self.select, name)
            btn.append_child(UIImage(Rect((0, 0), btn.relative_bounds.size), None, self.units[name].icon))

            self.append_child(btn)
            i += 1
        self.selected_unit = unit.unit_id

    def select(self, name):
        self.game.send([Game.ServerCommands.PRODUCE_UNIT, self.selected_unit, name])

    def draw(self, screen):
        super().draw(screen)

    def update(self, event):
        if super().update(event):
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            collide = self.game.collide_cursor(event.pos)
            for unit in collide:
                if isinstance(unit, ProducingBuilding) and unit.team == self.game.current_team:
                    self.set_selected(unit)
                    break

        # if self.selected:
        #     if event.type == pygame.MOUSEBUTTONUP:
        #         if event.button == 1:
        #             self.game.place_building(self.selected.name, pygame.mouse.get_pos())
        #             return True
        #         if event.button == 3:
        #             self.selected = None
        #             return True
        return False


class ResourceMenu(UIElement):
    def __init__(self, player, bounds, font):
        super().__init__(bounds, None)
        self.money_count = Label(Rect(0, 0, 500, 500), Color('yellow'), font, '-')
        self.append_child(self.money_count)
        self.wood_count = Label(Rect(105, 0, 500, 500), Color('brown'), font, '-')
        self.append_child(self.wood_count)
        self.meat_count = Label(Rect(220, 0, 500, 500), Color('red'), font, '-/-')
        self.append_child(self.meat_count)
        self.player = player

    def update(self, event):
        if super().update(event):
            return True
        self.update_values()

    def update_values(self):
        self.money_count.set_text(f'{self.player.money}')
        self.wood_count.set_text(f'{self.player.wood}')
        self.meat_count.set_text(f'{self.player.meat}/{self.player.max_meat}')
