from typing import Optional, Callable

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.font import Font
from pygame.rect import Rect

from src.constants import EVENT_SEC, EVENT_UPDATE


class UIElement:
    def __init__(self, bounds: Rect, color: Optional[Color], border_top_left_radius=-1, border_top_right_radius=-1,
                 border_bottom_left_radius=-1, border_bottom_right_radius=-1):
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        self.relative_bounds = bounds
        self.absolute_bounds = bounds.copy()
        self.color = color
        self.childs = []
        self.enabled = True
        self.parent = None

    def update_bounds(self):
        self.absolute_bounds = self.relative_bounds.copy()
        self.absolute_bounds.x = self.absolute_x
        self.absolute_bounds.y = self.absolute_y

        for child in self.childs:
            child.update_bounds()

    @property
    def absolute_x(self):
        if self.parent is None:
            return self.relative_bounds.x
        return self.relative_bounds.x + self.parent.absolute_x

    @property
    def absolute_y(self):
        if self.parent is None:
            return self.relative_bounds.y
        return self.relative_bounds.y + self.parent.absolute_y

    def move(self, x, y):
        self.relative_bounds.move_ip(x, y)
        self.update_bounds()

    def update(self, event: Event):
        for elem in reversed(self.childs):
            if elem.enabled and elem.update(event):
                return True
        return False

    def render(self, screen: Surface):
        self.draw(screen)
        for elem in self.childs:
            if elem.enabled:
                elem.render(screen)

    def draw(self, screen: Surface):
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.absolute_bounds,
                             border_top_left_radius=self.border_top_left_radius,
                             border_top_right_radius=self.border_top_right_radius,
                             border_bottom_left_radius=self.border_bottom_left_radius,
                             border_bottom_right_radius=self.border_bottom_right_radius,
                             )

    def append_child(self, child):
        self.childs.append(child)
        child.parent = self
        child.update_bounds()

    def shutdown(self):
        pass


class Label(UIElement):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str):
        self.font = font
        self.text = text
        self.text_image = self.font.render(self.text, True, color)
        if bounds.width == 0 and bounds.height == 0:
            bounds.size = self.text_image.get_size()
        super().__init__(bounds, color)

    def update_text(self):
        self.text_image = self.font.render(self.text, True, self.color)

    def set_text(self, text: str):
        if self.text != text:
            self.text = text
            self.update_text()

    def set_color(self, color: Color):
        if self.color != color:
            self.color = color
            self.update_text()

    def draw(self, screen):
        screen.blit(self.text_image, self.absolute_bounds)


class FPSCounter(Label):
    def __init__(self, bounds: Rect, font: Font):
        super().__init__(bounds, Color('green'), font, 'FPS:')
        self.frames = 0

    def update(self, event):
        if event.type == EVENT_SEC:
            self.set_text(f'FPS: {self.frames}')
            self.frames = 0

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.frames += 1


class UIImage(UIElement):
    def __init__(self, bounds, image_path, image=None):
        super().__init__(bounds, None)
        self.image = pygame.image.load(image_path) if (image_path is not None) else image
        if bounds.width != 0 and bounds.height != 0:
            self.image = pygame.transform.smoothscale(self.image, self.relative_bounds.size)

    def draw(self, screen):
        screen.blit(self.image, self.absolute_bounds.topleft)


class UIButton(UIElement):
    def __init__(self, bounds, color, callback_func, *func_args,
                 on_mouse_hover=None,
                 on_mouse_exit=None):
        super().__init__(bounds, color)
        self.callback_func: Callable = callback_func
        self.callback_args = func_args

        self.hovered = False
        self.on_mouse_hover = on_mouse_hover or (lambda: None)
        self.on_mouse_exit = on_mouse_exit or (lambda: None)

    def update(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.absolute_bounds.collidepoint(*mouse_pos):
                if not self.hovered:
                    self.hovered = True
                    self.on_mouse_hover()
            else:
                if self.hovered:
                    self.hovered = False
                    self.on_mouse_exit()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.absolute_bounds.collidepoint(*event.pos):
                self.callback_func(*self.callback_args)
                return True


class UIPopup(Label):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str, lifetime: int):
        super().__init__(bounds, color, font, text)
        self.life_time = lifetime

    def update(self, event):
        if event.type == EVENT_UPDATE:
            self.life_time -= 1
            if self.life_time <= 0:
                self.parent.childs.remove(self)
                return
        super().update(event)
