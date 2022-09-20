import math
import random
from enum import Enum
from typing import Tuple, Any

import pygame
from pygame import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite

from src.constants import EVENT_UPDATE, EVENT_SEC


class Unit(Sprite):

    def __init__(self, game, name, x, y, unit_id, team):
        self.unit_id = unit_id
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
        self.game.update_health_info(self)


class TwistUnit(Unit):
    def __init__(self, game, name, x, y, unit_id, team=-1):
        super().__init__(game, name, x, y, unit_id, team)
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
    def __init__(self, game, name, x, y, unit_id, team=-1):
        super().__init__(game, name, x, y, unit_id, team)
        self.lifetime = self.cls_dict['lifetime']
        self.damage = self.cls_dict.get('damage', 0)

    def update(self, event):
        super().update(event)
        if event.type == EVENT_UPDATE:
            self.move_to_angle()
            if self.game.side == self.game.Side.SERVER:
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

    def __init__(self, game, name, x, y, unit_id, team=-1):
        super().__init__(game, name, x, y, unit_id, team)
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
        if self.game.side is self.game.Side.SERVER:
            self.delay -= 1

    def update(self, event):
        super().update(event)
        if (event.type == EVENT_SEC) and (self.game.side is self.game.Side.SERVER):
            if self.target[0] is Fighter.Target.NONE:
                self.find_new_target()
        if event.type == EVENT_UPDATE:
            if self.target[0] is Fighter.Target.ATTACK:
                if self.game.side == self.game.Side.SERVER and self.target[1].dead:
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
        if self.game.side is self.game.Side.SERVER:
            if self.delay <= 0:
                self.delay = self.delay_time

                self.target[1].take_damage(self.damage)

    def throw_projectile(self, name):
        if self.game.side is self.game.Side.SERVER:
            if self.delay <= 0:
                self.game.create_unit(name, (self.x, self.y), self.team, angle=self.angle)
                self.delay = self.delay_time

    def move_to_point(self):
        self.find_target_angle()
        self.turn_around()
        self.move_to_angle()
        if self.game.side is self.game.Side.SERVER:
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
    def __init__(self, game, name, x, y, unit_id, team=-1):
        super().__init__(game, name, x, y, unit_id, team)
        self.valid_types = self.cls_dict['valid_types']
        self.produce_time = self.cls_dict['produce_time']
        self.time = self.produce_time
        self.units_tray = []

    def add_to_queue(self, name):
        if name not in self.cls_dict['valid_types']:
            print(f'{self.unit_id} can not produce {name}')
            return
        print(self.game.get_player(self.team))
        self.game.get_player(self.team).spend({'money': 2})
        self.units_tray.append(name)
        print(self.units_tray)

    def update(self, event):
        super().update(event)

        if self.game.side is self.game.Side.SERVER and event.type == EVENT_SEC and self.units_tray:
            if self.time > 0:
                self.time -= 1
            elif self.time == 0:
                unit = self.units_tray.pop(0)
                self.time = self.produce_time
                self.game.create_unit(unit, self.pos_around, self.team)
                print('created')
