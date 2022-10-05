import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.time import Clock

from src.config import config
from src.constants import EVENT_SEC, EVENT_UPDATE
from src.main_menu import MainMenu
from src.ui import UIElement


class Main:
    def __init__(self, main_element: UIElement, screen: Surface):
        self.main_element = main_element
        self.screen = screen
        self.running = True

    @property
    def main_element(self):
        return self._main_element

    @main_element.setter
    def main_element(self, value: UIElement):
        self._main_element = value
        value.main = self

    def loop(self):
        clock = Clock()

        pygame.time.set_timer(EVENT_UPDATE, 1000 // 60)
        pygame.time.set_timer(EVENT_SEC, 1000 // 1)

        while self.running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    print('Exit')
                    self.main_element.shutdown()
                    print('Shutdowned')
                    return
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        print('Exit')
                        self.main_element.shutdown()
                        print('Shutdowned')
                        return

                self.main_element.update(event)

            self.screen.fill((0, 0, 0))
            self.main_element.render(self.screen)

            pygame.display.flip()
            clock.tick(60)

        self.main_element.shutdown()


def main():
    pygame.init()
    screen = pygame.display.set_mode(config.screen.size, pygame.FULLSCREEN if config.screen.fullscreen else 0)

    elem = MainMenu(Rect((0, 0), config.screen.size))

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
