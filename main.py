import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.time import Clock

from constants import SCREEN_SIZE, EVENT_SEC, EVENT_UPDATE
from ui import UIElement, FPSCounter


class Main:
    def __init__(self, main_element: UIElement, screen):
        self.main_element = main_element
        self.screen = screen

    def loop(self):
        clock = Clock()

        running = True

        pygame.time.set_timer(EVENT_UPDATE, 1000 // 60)
        pygame.time.set_timer(EVENT_SEC, 1000 // 1)

        while running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    print('Exit')
                    return
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        print('Exit')
                        return

                self.main_element.update(event)

            self.screen.fill((0, 0, 0))
            self.main_element.render(self.screen)

            pygame.display.flip()
            clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    elem = UIElement(Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]), Color('aquamarine3'))

    fps_font = pygame.font.Font('src/fonts/arial.ttf', 20)

    sub_elem = UIElement(Rect(50, 50, 50, 50), None)
    sub_elem.append_child(FPSCounter(Rect(50, 50, 0, 0), fps_font))
    elem.append_child(sub_elem)

    m = Main(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
