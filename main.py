import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.time import Clock

from config import config
from constants import EVENT_SEC, EVENT_UPDATE
from main_menu import MainMenu
from ui import UIElement


class Main:
    def __init__(self, main_element: UIElement, screen):
        self.main_element = main_element
        self.screen = screen

    @property
    def main_element(self):
        return self._main_element

    @main_element.setter
    def main_element(self, value):
        self._main_element = value
        value.main = self

    def loop(self):
        clock = Clock()

        running = True

        pygame.time.set_timer(EVENT_UPDATE, 1000 // 60)
        pygame.time.set_timer(EVENT_SEC, 1000 // 1)

        while running:
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


def main():
    pygame.init()
    screen = pygame.display.set_mode(config['screen']['size'])

    elem = MainMenu(Rect((0, 0), config['screen']['size']), Color('aquamarine3'))

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
