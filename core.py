import random
from builtins import print
from enum import Enum, auto
from functools import wraps
from multiprocessing.connection import PipeConnection

import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.sprite import Group, Sprite

from config import config
from constants import EVENT_UPDATE, EVENT_SEC
from ui import UIElement


class Camera:
    def __init__(self, game):
        self.offset_x = 0
        self.offset_y = 0
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

    def __init__(self, game, x, y):
        self.rect = Rect(0, 0, 50, 50)
        self.game = game
        self.pos_x = x
        self.pos_y = y
        self.rect.center = self.pos_x, self.pos_y
        if game.side == Game.Side.SERVER:
            self.unit_id = Unit.next_id
            Unit.next_id += 1
        super().__init__()

    def update(self, event):
        pass
        # self.move(0, 1)

    def move(self, x, y):
        self.pos_x += x
        self.pos_y += y
        self.rect.center = self.pos_x, self.pos_y

    def draw(self, screen, camera):
        pygame.draw.rect(screen, Color('red'), self.rect.move(camera.offset_x, camera.offset_y))
        pygame.draw.rect(screen, Color('black'), self.rect.move(camera.offset_x, camera.offset_y), 2)


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

    def __init__(self, side: Side, **kwargs):
        self.side = side
        self.sprites = Group()
        self.world_size = config['world']['size']
        self.world_rect = Rect(-self.world_size, -self.world_size, self.world_size * 2, self.world_size * 2)
        if self.side == Game.Side.SERVER:
            self.send_connection: PipeConnection = kwargs['send_connection']
            self.next_sync = 10

    def update(self, event):
        self.sprites.update(event)

        if self.side == Game.Side.SERVER:
            if event.type == EVENT_SEC:
                self.next_sync -= 1
                if random.randint(0, 100) < 25:
                    self.create_entity()
                    print('Created')
                if self.next_sync <= 0:
                    self.next_sync = 10
                    self.sync()

    def find_with_id(self, unit_id: int):
        for u in self.sprites:
            if u.unit_id == unit_id:
                return u

    @side_only(Side.SERVER)
    def sync(self):
        print('Sync')
        for unit in self.sprites:
            self.send_connection.send(f'2~<class_id>~{unit.unit_id}~{unit.pos_x}~{unit.pos_y}')

    @side_only(Side.SERVER)
    def create_entity(self):
        u = Unit(self, random.randint(-self.world_size, self.world_size), random.randint(-self.world_size, self.world_size))
        self.sprites.add(u)
        self.send_connection.send(f'1~<class_id>~{u.unit_id}~{u.pos_x}~{u.pos_y}')

    @side_only(Side.CLIENT)
    def handle_command(self, command, args):
        if command == '1':
            print('1', args)
            u = Unit(self, int(args[2]), int(args[3]))
            u.unit_id = int(args[1])
            self.sprites.add(u)

        elif command == '2':
            print('2', args)
            u = self.find_with_id(int(args[1]))
            if u is not None:
                u.pos_x = int(args[2])
                u.pos_y = int(args[3])
                u.rect.center = u.pos_x, u.pos_y
            else:
                u = Unit(self, int(args[2]), int(args[3]))
                u.unit_id = int(args[1])
                self.sprites.add(u)
        else:
            print('Unexpected command', args)


class Minimap(UIElement):
    def __init__(self, game: Game, camera: Camera):
        self.game = game
        self.camera = camera
        self.mark_size = config['minimap']['mark_size']
        self.mark_color = Color(*config['minimap']['mark_color'])
        super().__init__(Rect(*config['minimap']['bounds']), Color(*config['minimap']['color']))

    def draw(self, screen):
        super().draw(screen)
        mark_rect = Rect(self.absolute_bounds.x, self.absolute_bounds.y, self.mark_size, self.mark_size)
        for unit in self.game.sprites:
            pos = self.worldpos_to_minimap(unit.pos_x, unit.pos_y)
            mark_rect.centerx = self.absolute_bounds.x + pos[0]
            mark_rect.centery = self.absolute_bounds.y + pos[1]
            pygame.draw.ellipse(screen, self.mark_color, mark_rect)

        camera_rect = Rect(
            (self.game.world_size - self.camera.offset_x) * self.world_ratio_width,
            (self.game.world_size - self.camera.offset_y) * self.world_ratio_height,
            config['screen']['size'][0] * self.world_ratio_width,
            config['screen']['size'][1] * self.world_ratio_height
        )
        pygame.draw.rect(screen, Color('yellow'), camera_rect.move(self.absolute_bounds.x, self.absolute_bounds.y), 1)

        pygame.draw.rect(screen, Color('green'), self.game.world_rect.move(self.camera.offset_x, self.camera.offset_y),
                         2)

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
